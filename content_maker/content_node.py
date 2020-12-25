#!/usr/bin/env python3

from types import MethodType
from collections import OrderedDict
from PyQt5.QtWidgets import QWidget, QMessageBox, QAction, QListWidgetItem, QMenu
from PyQt5.QtCore import Qt

from .views.character_content_node_view import Ui_character_content_node
from .metas import ISerializable, Dirty
from .icon_generator import IconGenerator


class CharacterContentNode(QWidget, Ui_character_content_node, ISerializable, Dirty):
	
	def __init__(self, db_list, parent=None, flags=Qt.WindowFlags()):
		super().__init__(parent=parent, flags=flags)
		Dirty.__init__(self)
		self.db_list = db_list
		self.setupUi(self)

	def __str__(self):
		return "content_node"

	def setupUi(self, character_content_node):
		super().setupUi(character_content_node)
		# route drops signals
		self.character_list.itemChanged.connect(self.onCharacterDrop)
		self.drops_list.itemChanged.connect(self.onWorldObjectDrop)
		self.merchandise_list.itemChanged.connect(self.onWorldObjectDrop)
		self.spells_list.itemChanged.connect(self.onSpellsDrop)
		# setup delete button function
		self.on_delete_confirm = QAction()
		self.delete_node_bttn.clicked.connect(self.deleteNode)
		# route context menu operations
		list_widgets = [self.character_list, self.drops_list, self.merchandise_list, self.spells_list]
		for list_widget in list_widgets:
			list_widget.contextMenuEvent = MethodType(self.onListContextMenu, list_widget)

	def onListContextMenu(self, list_widget, QContextMenuEvent):
		# get select item
		row = list_widget.indexAt(QContextMenuEvent.pos()).row()
		# create context menu
		menu = QMenu(self)
		# create actions
		move_up_action = QAction("Move Up",
			triggered=lambda: list_widget.insertItem(row - 1, list_widget.takeItem(row)))
		move_down_action = QAction("Move Down",
			triggered=lambda: list_widget.insertItem(row + 1, list_widget.takeItem(row)))
		delete_action = QAction("Delete",
			triggered=lambda: list_widget.takeItem(row))
		if row > 0:
			menu.addAction(move_up_action)
		if row < list_widget.count() - 1:
			menu.addAction(move_down_action)
		menu.addSeparator()
		menu.addAction(delete_action)
		# exec actionrow
		action = menu.exec_(QContextMenuEvent.globalPos())

	def deleteNode(self, bypass_prompt=False):
		self.setAttribute(Qt.WA_DeleteOnClose)
		if bypass_prompt:
			self.on_delete_confirm.trigger()
			self.close()
		else:
			reply = QMessageBox.question(self, "Delete Node",
				"Delete Node?", QMessageBox.Yes | QMessageBox.No)
			if reply == QMessageBox.Yes:
				self.on_delete_confirm.trigger()
				self.close()
		
	def deleteCharacter(self, list_widget, listWidgetItem):
		# delete character entry
		if self.db_list.isCharacter(listWidgetItem.text()):
			list_widget.takeItem(list_widget.count() - 1)

	def onCharacterDrop(self, listWidgetItem):
		# only one character allowed here
		row = self.character_list.count() - 1
		if not self.db_list.isCharacter(listWidgetItem.text()):
			self.character_list.takeItem(row)
		elif self.character_list.count()> 1:
			self.character_list.takeItem(row - 1)

	def onWorldObjectDrop(self, listWidgetItem):
		# allow anything other then characters
		def deleteCharacter(list_widget, listWidgetItem):
			if self.db_list.isCharacter(listWidgetItem.text()):
				list_widget.takeItem(list_widget.count() - 1)
		deleteCharacter(self.drops_list, listWidgetItem)
		deleteCharacter(self.merchandise_list, listWidgetItem)
		self.removeDuplicates(self.merchandise_list)
		self.removeDuplicates(self.drops_list)

	def onSpellsDrop(self, listWidgetItem):
		# allow only spells here
		if not self.db_list.isSpell(listWidgetItem.text()):
			self.spells_list.takeItem(self.spells_list.count() - 1)
		self.removeDuplicates(self.spells_list)

	def removeDuplicates(self, list_widget):
		entryNames = [list_widget.item(i).text() for i in range(list_widget.count())]
		if len(entryNames) != len(set(entryNames)):
			list_widget.takeItem(list_widget.count() - 1)

	def routeDirtiables(self, parent):
		self.onDirty = QAction(triggered=lambda: parent.setDirty([]))
		self.move_node_left_bttn.clicked.connect(parent.setDirty)
		self.move_node_right_bttn.clicked.connect(parent.setDirty)

		self.character_list.itemChanged.connect(parent.setDirty)
		self.level.valueChanged.connect(parent.setDirty)
		self.enemy.stateChanged.connect(parent.setDirty)
		self.healer.stateChanged.connect(parent.setDirty)
		self.healer_gold_amount.valueChanged.connect(parent.setDirty)
		self.dialogue.textChanged.connect(parent.setDirty)
		self.drops_list.itemChanged.connect(parent.setDirty)
		self.spells_list.itemChanged.connect(parent.setDirty)
		self.merchandise_list.itemChanged.connect(parent.setDirty)

	def serialize(self):

		def getItemData(list_widget, singular=False):
			itemData = []
			for i in range(list_widget.count()):
				entry_text = list_widget.item(i).text()
				itemData.append([entry_text, \
					self.db_list.getEntryIconSource(entry_text)])
			if singular and len(itemData) > 0:
				return itemData[0]
			return itemData

		payload = OrderedDict([
			("character", getItemData(self.character_list, True)),
			("level", self.level.value()),
			("enemy", self.enemy.isChecked()),
			("healer", self.healer.isChecked()),
			("healerCost", self.healer_gold_amount.value()),
			("dialogue", self.dialogue.toPlainText()),
			("drops", getItemData(self.drops_list)),
			("spells", getItemData(self.spells_list)),
			("merchandise", getItemData(self.merchandise_list))
		])
	
		return payload

	def unserialize(self, data):

		icon_generator = IconGenerator()
		def unpackItemData(list_widget, serialized_list_data):
			icon = icon_generator.getIcon(serialized_list_data[1])
			list_widget.addItem(QListWidgetItem(icon, serialized_list_data[0]))

		if len(data["character"]) != 0:
			unpackItemData(self.character_list, data["character"])

		self.level.setValue(int(data["level"]))
		self.enemy.setChecked(bool(data["enemy"]))
		self.healer.setChecked(bool(data["healer"]))
		self.healer_gold_amount.setValue(int(data["healerCost"]))
		self.dialogue.setText(data["dialogue"])

		for drop in data["drops"]:
			unpackItemData(self.drops_list, drop)

		for spell in data["spells"]:
			unpackItemData(self.spells_list, spell)

		for merchandise in data["merchandise"]:
			unpackItemData(self.merchandise_list, merchandise)

