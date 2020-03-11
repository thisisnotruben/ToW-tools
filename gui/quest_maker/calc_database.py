import os

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from calc_conf import *
from node_editor.utils import dumpException

from exporters.game_db import GameDB, DataBases
from exporters.tiled_manager import Tiled
from exporters.path_manager import PathManager


class DataEntry(QListWidgetItem):
    def __init__(self, data, index, QIcon, str, parent=None, type=QListWidgetItem.Type):
        super().__init__(QIcon, str, parent=parent, type=type)
        self.data = data
        self.index = index

    def __hash__(self):
        return self.index


class DataView(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.icon_atlas = QPixmap("/home/rubsz/tiled/Tides_of_War/non_map/assets/dev_icon/icons.png")
        self.icon_size = (16, 16)
        self.character_tag = "Character"
        self.all_items = set()
        self.type_tags = {}
        self.sub_type_tags = {}
        self.initUI()
        self.load_databases()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.search = QLineEdit(parent=self)
        self.search.textChanged.connect(self.onSearch)
        self.search.setPlaceholderText("Find")

        self.filter_db = QComboBox(self)
        self.filter_db.addItem("All")
        self.filter_db.currentTextChanged.connect(self.onFilterDb)

        self.filter_type = QComboBox(self)
        self.filter_type.addItem("All")
        self.filter_type.hide()
        self.filter_type.currentTextChanged.connect(self.onFilterSearch)

        self.filter_sub_type = QComboBox(self)
        self.filter_sub_type.addItem("All")
        self.filter_sub_type.hide()
        self.filter_sub_type.currentTextChanged.connect(self.onFilterSearch)

        self.list_view = QListWidget(self)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setTabKeyNavigation(True)

        self.layout.addWidget(self.search)
        self.layout.addWidget(self.filter_db)
        self.layout.addWidget(self.filter_type)
        self.layout.addWidget(self.filter_sub_type)
        self.layout.addWidget(self.list_view)

    def load_databases(self):
        db_path = PathManager.get_paths()["db"]
        game_db = GameDB(db_path)
        item_data = game_db.get_database(DataBases.ITEMDB)
        spell_data = game_db.get_database(DataBases.SPELLDB)

        db_path = PathManager.get_paths()["tiled"]
        character_data = Tiled(db_path).get_character_data()

        db_tags = [self.character_tag, DataBases.ITEMDB.value, DataBases.SPELLDB.value]
        db_tags.sort()

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

        self.clear_database()
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

        self.filter_db.addItems(db_tags)

    def clear_database(self):
        while self.list_view.count() != 0:
            self.list_view.removeItemWidget(self.list_view.item(0))
    
    def clear_combo_box(self, combo_box):
        while combo_box.count() != 1:
            combo_box.removeItem(1)
    
    def onSearch(self, current_text):
        founded_items = set(self.list_view.findItems(current_text, Qt.MatchContains))

        db_filter = self.filter_db.currentText()
        if db_filter != "All":
            founded_items = set([entry for entry in founded_items if entry.data["_DB"] == db_filter])

        type_filter = self.filter_type.currentText()
        if self.filter_type.isVisible() and type_filter != "All":
            founded_items = set([entry for entry in founded_items if entry.data["_TYPE"].capitalize() == type_filter])

        sub_type_filter = self.filter_sub_type.currentText()
        if self.filter_sub_type.isVisible() and sub_type_filter != "All":
            founded_items = set([entry for entry in founded_items if "_SUB_TYPE" in entry.data and entry.data["_SUB_TYPE"] == sub_type_filter])
        
        for entry in founded_items:
            entry.setHidden(False)
        for entry in self.all_items - founded_items:
            entry.setHidden(True)

    def onFilterDb(self, text):
        if text == DataBases.SPELLDB.value or text == "All":
            self.filter_type.hide()
            self.filter_sub_type.hide()
        else:
            self.clear_combo_box(self.filter_type)
            self.filter_type.addItems(self.type_tags[self.filter_db.currentText()])
            self.filter_type.show()
            self.filter_sub_type.hide()
            if text == self.character_tag:
                self.clear_combo_box(self.filter_sub_type)
                self.filter_sub_type.addItems(self.sub_type_tags[self.filter_db.currentText()])
                self.filter_sub_type.show()
        self.onFilterSearch(text)
    
    def onFilterSearch(self, text):
        self.onSearch(self.search.text())

    def addItem(self, data, icon_data, label):
        icon = None
        if type(icon_data) == int:
            width = self.icon_atlas.width() / self.icon_size[0]
            rect = QRect(icon_data % width * self.icon_size[0], icon_data // width * self.icon_size[1], *self.icon_size)
            icon = QIcon(self.icon_atlas.copy(rect))    
        else:
            icon = QIcon(icon_data)
        entry = DataEntry(data, self.list_view.count(), icon, label, self.list_view)
        self.list_view.addItem(entry)
        self.all_items.add(entry)
