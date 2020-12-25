#!/usr/bin/env python3

import os
from types import MethodType
from collections import OrderedDict
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QAction, QMessageBox
from PyQt5.QtGui import QIcon

from .views.quest_node_objective_view import Ui_quest_objective_view
from .metas import ISerializable, Dirty
from .icon_generator import IconGenerator
from .quest_character_content import QuestCharacterContent


class QuestObjective(Ui_quest_objective_view, QWidget, ISerializable, Dirty):
	def __init__(self, parent, db_list, data={}):
		super().__init__()
		Dirty.__init__(self)
		self.setParent(parent)
		self.db_list = db_list
		self.wildcard = {"active" : False, "virgin_world_object_name": ""}
		self.setupUi(self)
		self.show()

	def setupUi(self, Form):
		super().setupUi(Form)
		# route list drop event to this class
		self.world_object_drop_event = self.world_object.dropEvent
		self.world_object.dropEvent = MethodType(self.onDropEvent, self.world_object)
		# setup character content
		self.character_content = QuestCharacterContent(self.db_list)
		self.character_content.routeDirtiables(self)
		icon = QIcon(os.path.join(os.path.dirname(__file__), os.pardir, "icon.png"))
		self.character_content.setWindowIcon(icon)
		self.quest_type.currentTextChanged.connect(self.onQuestTypeCurrentTextChanged)
		self.extra_content_bttn.clicked.connect(self.onExtraContentBttnClicked)

	def isEmpty(self):
		return self.world_object.count() == 0

	def onDropEvent(self, list_widget, event):
		# only one entry allowed
		self.world_object_drop_event(event)
		if list_widget.count() > 1:
			list_widget.takeItem(0)
		# add ability for more content
		is_character = self.db_list.isCharacter(self.getWorldObjectName())
		self.extra_content_bttn.setDisabled(not is_character)
		self.world_object_keep.setDisabled(is_character)
		if is_character:
			self.world_object_keep.setChecked(False)
		# util function
		def reset():
			self.wildcard["active"] = False
			self.wildcard["virgin_world_object_name"] = ""
			self.amount.setValue(1)
			self.amount.setDisabled(True)
		# if character name is not unique ask if you want this character
		# in particular, or all units with this name
		entry_name = self.getWorldObjectName()
		if not self.db_list.isEntryUnique(entry_name):            
			reply = QMessageBox.question(self, "Duplicate found in world ─ Tides of War", \
				"World object is mentioned more than once in game. "
				"Include all world objects with this name, or just "
				"this specific world object?",
				QMessageBox.YesToAll | QMessageBox.Yes | QMessageBox.Cancel)
			# route reply
			if reply == QMessageBox.Yes:
				reset()
			elif reply == QMessageBox.YesToAll:
				entry = self.world_object.item(0)
				self.wildcard["active"] = True
				self.wildcard["virgin_world_object_name"] = entry.text()
				entry.setText(self.db_list.getEntryNameToGameName(entry.text()))
			elif reply == QMessageBox.Cancel:
				self.delete_self = True
		# spells and unique characters can only have an amount one
		elif self.db_list.isSpell(entry_name) \
		or (self.db_list.isCharacter(entry_name) \
		and self.db_list.isEntryUnique(entry_name)):
			reset()
		# set quest types in combo box
		while self.quest_type.count() != 0:
			self.quest_type.removeItem(0)
		self.quest_type.addItems(
			[
				tag.capitalize()
				for tag in self.db_list.getQuestTypeTags(entry_name)
			]
		)

	def onExtraContentBttnClicked(self):
		self.character_content.setWindowTitle("%s \u2015 Tides of War" % self.getWorldObjectName())
		self.character_content.show()
		self.character_content.move(
			self.mapToGlobal((self.parentWidget().pos())))

	def onQuestTypeCurrentTextChanged(self, text):
		# only hardcoded value here, so watch out
		self.extra_content_bttn.setDisabled(text.lower() != "talk")
	
	def routeDirtiables(self, parent):
		self.onDirty = QAction(triggered=lambda: parent.setDirty([]))
		self.world_object.itemChanged.connect(parent.setDirty)
		self.world_object_keep.stateChanged.connect(parent.setDirty)
		self.quest_type.currentIndexChanged.connect(parent.setDirty)
		self.amount.valueChanged.connect(parent.setDirty)

	def getWorldObjectName(self):
		world_object = self.world_object.item(0)
		return world_object.text() if world_object != None else ""

	def serialize(self):
		self.dirty = False
		payload = OrderedDict([
			("worldObject", [self.getWorldObjectName(), -1]),
			("keepWorldObject", self.world_object_keep.isChecked()),
			("questType", self.quest_type.currentText().lower()),
			("amount", self.amount.value()),
			("wildcard", OrderedDict(self.wildcard)),
			("extraContent", self.character_content.serialize())
		])
		if payload["worldObject"][0] != "":
			icon = self.db_list.getEntryIconSource(payload["worldObject"][0])
			if icon == -1:
				icon = self.db_list.getEntryIconSource(self.wildcard["virgin_world_object_name"])
			payload["worldObject"] = [payload["worldObject"][0], icon]
		return payload

	def unserialize(self, data):
		# set world object
		if data["worldObject"][0] != "":
			icon = IconGenerator().getIcon(data["worldObject"][1])
			self.world_object.addItem(QListWidgetItem(icon, data["worldObject"][0]))
			self.world_object_keep.setDisabled(self.db_list.isCharacter(data["worldObject"][0]))
			# set quest type
			self.quest_type.addItems([
					tag.capitalize()
					for tag in self.db_list.getQuestTypeTags(data["worldObject"][0])
			])
			self.quest_type.setCurrentText(data["questType"].capitalize())
		# set keep world object
		self.world_object_keep.setChecked(bool(data["keepWorldObject"]))
		# set amount
		self.amount.setValue(int(data["amount"]))
		# set generic data
		self.wildcard["virgin_world_object_name"] = data["wildcard"]["virgin_world_object_name"]
		self.wildcard["active"] = bool(data["wildcard"]["active"])
		self.amount.setDisabled(not self.wildcard["active"])
		# set character content data
		self.character_content.unserialize(data["extraContent"])

