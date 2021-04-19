#!/usr/bin/env python3

import os
import re
import json
from collections import Counter
from typing import *

from PyQt5.QtCore import Qt, QRect, QSize, QMimeData
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from .icon_generator import IconGenerator

from core.game_db import GameDB, DataBases
from core.tiled_manager import Tiled
from core.path_manager import PathManager
from core.game_dialogue import GameDialogue


class DataView(QListWidget):
	def __init__(self, parent=None):
		super().__init__(parent=parent)

		self.icon_generator = IconGenerator()
		self.game_db = GameDB()

		self.all_items = {}
		self.allDialogues: List[str] = []
		self.allQuests: List[str] = []
		# used for the combo boxes in searching
		self.character_tag: str = "Character"
		self.dialogue_tag: str = "Dialogue"
		self.quest_tag: str = "Quest"

		self.db_tags: List[str] = []
		self.type_tags: Dict[str, List[str]] = {}
		self.sub_type_tags = {}
		# used for the combo boxes in the objective entry combo boxes
		self.quest_types = PathManager.get_paths()["quest_maker_tags"]
		# load self
		self.initUI()
		self.load_databases()

	def initUI(self) -> None:
		self.setObjectName("list_view")
		self.setAlternatingRowColors(True)
		self.setDragEnabled(True)

	def load_databases(self) -> None:
		self.db_tags = sorted([self.character_tag, self.dialogue_tag, self.quest_tag, "Item", "Spell"])

		self.type_tags[DataBases.ITEMDB.value.capitalize()] = [itemType[0].capitalize() for itemType in
			self.game_db.execute_query(
				"SELECT DISTINCT type FROM worldobject, item "
				"WHERE worldObject.name = item.name ORDER BY type;")]
		self.type_tags[DataBases.SPELLDB.value.capitalize()] = []

		character_data = Tiled().get_character_data()
		characterTags: set = set()
		characterRaces: set = set()
		for cPacket in character_data:
			characterTags.add(cPacket["map"])
			characterRaces.add(cPacket["race"])

		self.type_tags[self.character_tag] = sorted(list(characterTags))
		self.sub_type_tags[self.character_tag] = sorted(list(characterRaces))

		self.clearDatabase()

		# add all items/spells to DB
		item_data = self.game_db.execute_query("SELECT icon, name FROM worldobject")
		for data in item_data:
			self.addItem({}, data[0], data[1])

		# add all characters to DB
		for cPacket in character_data:
			self.addItem(cPacket, cPacket["img"], "%s | %s" % (cPacket["editorName"], cPacket["map"]))

		# add all dialogue to DB
		self.allDialogues = []
		for dialogueName in GameDialogue().getDialogueNames():
			if re.match("q\d+(\.\d+)*", dialogueName, re.IGNORECASE):
				self.allDialogues.append(dialogueName)
				self.addItem({"dialogue": True}, 1015, dialogueName)

		# add all quests to DB
		self.allQuests = []

		questDir: str = PathManager.get_paths()["quest_content_dir"]
		for fileName in os.listdir(questDir):
			if not fileName.endswith("json"):
				continue

			with open(os.path.join(questDir, fileName), "r") as f:
				questData: Dict = json.load(f)
				if "node_type" not in questData \
				or questData["node_type"] != "QuestNode":
					continue

				for nodeData in questData["nodes"].values():
					questName: str = nodeData["questName"].strip()
					if questName != "":
						self.allQuests.append(questName)
						self.addItem({"quest":True}, 1006, questName)

	def addItem(self, data: Dict, icon_data, label: str):
		icon = self.icon_generator.getIcon(icon_data)
		entry = QListWidgetItem(icon, label, self)
		entry.setSizeHint(QSize(32, 32))
		entry.setData(Qt.UserRole, data)
		entry.setData(Qt.UserRole + 1, icon_data)
		self.all_items[label] = self.count() - 1
		super().addItem(entry)

	def clearDatabase(self):
		self.all_items = {}
		while self.count() != 0:
			self.takeItem(0)

	def isCharacter(self, entry_name):
		"""check if entry is a character. returns `bool`"""
		return len(self.game_db.execute_query(
			f"SELECT name FROM worldobject WHERE name = '{entry_name}'")) == 0 \
			and not self.isDialogue(entry_name) and not self.isQuest(entry_name)

	def isSpell(self, entry_name):
		return len(self.game_db.execute_query(
			f"SELECT name FROM spell WHERE name = '{entry_name}'")) > 0

	def isDialogue(self, entry_name: str) -> bool:
		return entry_name in self.allDialogues

	def isQuest(self, entry_name: str) -> bool:
		return entry_name in self.allQuests

	def isEntryUnique(self, entry_name):
		"""is the entry mentioned more then once in Database?
		returns `bool`"""
		# turn all database names to the actual game names
		formatted_names = map(self.getEntryNameToGameName, self.all_items.keys())
		entry_name = self.getEntryNameToGameName(entry_name)
		# if it equals zero, then item doesn't exist
		duplicate_finder = Counter(formatted_names)
		return duplicate_finder[entry_name] == 1

	def getEntryNameToGameName(self, entry_name):
		"""get whats shown in the game returns `str`"""
		return entry_name.split("-")[1] if "-" in entry_name else entry_name

	def getEntryIconSource(self, entry_name):
		"""Returns icon index `int` for atlas or filepath to image `str`"""
		if entry_name in self.all_items.keys():
			return self.item(self.all_items[entry_name]).data(Qt.UserRole + 1)
		return -1

	def getQuestTypeTags(self, entry_name):
		"""returns the quest type tags used
		for the combobox in the objective entries"""
		if self.isCharacter(entry_name):
			return self.quest_types["character"]
		elif self.isSpell(entry_name):
			return self.quest_types["spell"]
		else:
			return self.quest_types["item"]
