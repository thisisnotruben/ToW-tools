#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import os
from collections import Counter
from PyQt5.QtCore import Qt, QRect, QSize, QMimeData
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from quest_maker.icon_generator import IconGenerator

from core.game_db import GameDB, DataBases
from core.tiled_manager import Tiled


class DataEntry(QListWidgetItem):
    def __init__(self, index, QIcon, str, parent=None, type=QListWidgetItem.Type):
        super().__init__(QIcon, str, parent=parent, type=type)
        self.index = index

    def __hash__(self):
        return self.index


class DataView(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.icon_generator = IconGenerator()
        self.character_tag = "Character"
        self.all_items = set()
        self.db_tags = {}
        self.type_tags = {}
        self.sub_type_tags = {}
        self.initUI()
        self.load_databases()

    def initUI(self):
        self.setObjectName("list_view")
        self.setAlternatingRowColors(True)
        self.setDragEnabled(True)
        
    def load_databases(self):
        game_db = GameDB()
        item_data = game_db.get_database(DataBases.ITEMDB)
        spell_data = game_db.get_database(DataBases.SPELLDB)

        character_data = Tiled().get_character_data()

        self.db_tags = [self.character_tag, DataBases.ITEMDB.value, DataBases.SPELLDB.value]
        self.db_tags.sort()

        self.type_tags[DataBases.ITEMDB.value] = set([item_data[item_name]["type"]
            for item_name in item_data.keys()])
        self.type_tags[DataBases.ITEMDB.value] = [item_type.capitalize() 
            for item_type in self.type_tags[DataBases.ITEMDB.value]]
        self.type_tags[DataBases.ITEMDB.value].sort()
        
        self.type_tags[self.character_tag] = set()
        self.sub_type_tags[self.character_tag] = set()
        for character_id in character_data:
            character_race = os.path.splitext(
                os.path.basename(character_data[character_id]["img"]))[0].split("-")[0]
            character_data[character_id]["_TYPE"] = character_race
            character_data[character_id]["_SUB_TYPE"] = character_data[character_id]["map"].capitalize()
            character_data[character_id]["_DB"] = self.character_tag
            self.type_tags[self.character_tag].add(character_race.capitalize())
            self.sub_type_tags[self.character_tag].add(character_data[character_id]["_SUB_TYPE"])
        self.type_tags[self.character_tag] = list(self.type_tags[self.character_tag])
        self.type_tags[self.character_tag].sort()
        self.sub_type_tags[self.character_tag] = list(self.sub_type_tags[self.character_tag])
        self.sub_type_tags[self.character_tag].sort()

        while self.count() != 0:
            self.removeItemWidget(self.item(0))

        merged_data = {**item_data, **spell_data}
        for item_name in merged_data:
            merged_data[item_name]["_TYPE"] = merged_data[item_name]["type"]
            if item_name in spell_data.keys():
                merged_data[item_name]["_DB"] = DataBases.SPELLDB.value
            else:
                merged_data[item_name]["_DB"] = DataBases.ITEMDB.value
            self.addItem(merged_data[item_name], int(merged_data[item_name]["icon"]), item_name)
        
        for character_id in character_data:
            self.addItem(character_data[character_id], character_data[character_id]["img"],
                character_data[character_id]["editorName"])

    def addItem(self, data, icon_data, label):
        icon = self.icon_generator.getIcon(icon_data)
        entry = DataEntry(self.count(), icon, label, self)
        entry.setSizeHint(QSize(32, 32))
        entry.setData(Qt.UserRole, data)
        entry.setData(Qt.UserRole + 1, icon_data)
        super().addItem(entry)
        self.all_items.add(entry)

    def isCharacter(self, entry_name):
        return entry_name in [entry.text() for entry in self.all_items
            if entry.data(Qt.UserRole)["_DB"] == self.character_tag]

    def isSpell(self, entry_name):
        return entry_name in [entry.text() for entry in self.all_items
            if entry.data(Qt.UserRole)["_DB"] == DataBases.SPELLDB.value]

    def isEntryUnique(self, entry_name):
        # turn all database names to the actual game names
        formatted_names = [
            self.getEntryNameToGameName(entry.text())
            for entry in self.all_items
        ]
        entry_name = self.getEntryNameToGameName(entry_name)
        # if it equals zero, then item doesn't exist
        duplicate_finder = Counter(formatted_names)
        return duplicate_finder[entry_name] == 1

    def getEntryNameToGameName(self, entry_name):
        if "-" in entry_name:
            entry_name = entry_name.split("-")[1]
        return entry_name

    def getEntryIconSource(self, entry_name):
        for entry in self.all_items:
            if entry.text() == entry_name:
                return entry.data(Qt.UserRole + 1)
        return -1
        
