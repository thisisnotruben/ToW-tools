#!/usr/bin/env python3

import os
import sys
import json
from collections import OrderedDict
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QAction, QFileDialog, QPushButton
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtCore import Qt, QDir

from content_maker.views.main_view import Ui_content_maker_main
from content_maker.content_database import DataView
from content_maker.quest_node import QuestNode
from content_maker.content_node import CharacterContentNode
from content_maker.metas import ISerializable, Dirty
from content_maker.clipboard import Clipboard

from core.game_db import GameDB, DataBases
from core.path_manager import PathManager


class MainWindow(Ui_content_maker_main, QMainWindow, ISerializable, Dirty):
	def __init__(self, app):
		super().__init__()
		Dirty.__init__(self)

		self.clipboard = Clipboard()
		self.node = None
		self.nodes = []
		self.current_file = ""

		self.title = "Tides of War Content Maker"
		self.about = "Author: Ruben Alvarez Reyes<br/>Source: " \
			"<a href=\"https://github.com/thisisnotruben/ToW-tools/\">Github</a>"

		self.app = app
		self.setupUi(self)
		self.showMaximized()
		self.db = GameDB()

	def setupUi(self, MainWindow):
		super().setupUi(MainWindow)
		self.setTitle()
		# route actions
		self.action_undo.triggered.connect(lambda: self.onDo(False))
		self.action_redo.triggered.connect(lambda: self.onDo(True))
		self.undo_save_bttn.clicked.connect(lambda: self.onDo(False))
		self.redo_save_bttn.clicked.connect(lambda: self.onDo(True))
		self.disableUndoRedoActions()
		self.action_new.triggered.connect(self.onNewFile)
		self.action_open.triggered.connect(self.onOpenFile)
		self.action_save.triggered.connect(self.onSaveFile)
		self.action_save_As.triggered.connect(self.onSaveAsFile)
		self.action_quit.triggered.connect(self.close)

		# add about popup
		about_popup = lambda: QMessageBox.about(MainWindow, "About", self.about)
		self.action_about.triggered.connect(about_popup)
		# replace database widget
		self.list_view.setAttribute(Qt.WA_DeleteOnClose)
		self.list_view.hide()
		self.list_view = DataView(MainWindow)
		self.db_layout.addWidget(self.list_view)
		self.search.textChanged.connect(self.onSearch)
		self.reload_database_bttn.clicked.connect(self.list_view.load_databases)
		# route database combobox connections
		self.filter_db.addItem("All")
		self.filter_db.currentTextChanged.connect(self.onFilterDb)
		self.filter_db.addItems(self.list_view.db_tags)
		self.filter_type.addItem("All")
		self.filter_type.hide()
		self.filter_type.currentTextChanged.connect(
			lambda: self.onSearch(self.search.text()))
		self.filter_sub_type.addItem("All")
		self.filter_sub_type.hide()
		self.filter_sub_type.currentTextChanged.connect(
			lambda: self.onSearch(self.search.text()))
		# route clicked function
		self.add_node_bttn.clicked.connect(self.onNewFile)

	def setTitle(self):
		modified = self.isModified()
		header = self.title
		if os.path.isabs(self.current_file):
			header = "%s \u2015 %s" % \
				(os.path.basename(self.current_file), header)
		if modified: header = "*%s" % header
		self.setWindowTitle(header)

	def isModified(self):
		return not self.clipboard.isHistoryCurrent() or self.dirty

	def insertNode(self, index=0):
		self.setDirty([])
		# init widget
		node = self.node(self.list_view)
		node.routeDirtiables(self)
		# route button connections
		node.on_delete_confirm = QAction(
			triggered=lambda: self.onDeleteNodeConfirm(node))
		node.move_node_left_bttn.clicked.connect(
			lambda: self.onMoveNode(node, -1))
		node.move_node_right_bttn.clicked.connect(
			lambda: self.onMoveNode(node, 1))
		# add widget
		self.scroll_layout.insertWidget(index, node)
		self.nodes.insert(index, node)
		# name all node headers
		self.nodes_total_lbl.setText("Nodes: %d" % len(self.nodes))
		for i, n in enumerate(self.nodes):
			n.group_box.setTitle("Node %d" % i)
		# possibly disable move buttons
		# for node and neighbor nodes
		self.disableNodeMoveButtons(index)
		self.disableNodeMoveButtons(index - 1)
		self.disableNodeMoveButtons(index + 1)
		return node

	def deleteNode(self, node):
		node.deleteNode(True)

	def disableUndoRedoActions(self):
		# check index of buttons and
		# potentially disable buttons
		reached_end = self.clipboard.reached_end()
		self.action_undo.setDisabled(reached_end[0])
		self.action_redo.setDisabled(reached_end[1])
		self.undo_save_bttn.setDisabled(reached_end[0])
		self.redo_save_bttn.setDisabled(reached_end[1])

	def disableNodeMoveButtons(self, index):
		# disable move left/right buttons based on first/last index
		if index >= 0 and index < len(self.nodes):
			self.nodes[index].move_node_left_bttn.setDisabled( \
				index == 0)
			self.nodes[index].move_node_right_bttn.setDisabled( \
				index == len(self.nodes) - 1)

	def onDeleteNodeConfirm(self, node):
		self.setDirty([])
		index = self.nodes.index(node)
		self.nodes.remove(node)
		# name all node headers
		self.nodes_total_lbl.setText("Nodes: %d" % len(self.nodes))
		for i, n in enumerate(self.nodes):
			n.group_box.setTitle("Node %d" % i)
		self.scroll_layout.removeWidget(node)
		# possibly disable move buttons
		# for node and neighbor nodes
		self.disableNodeMoveButtons(index)
		self.disableNodeMoveButtons(index - 1)
		self.disableNodeMoveButtons(index + 1)

	def onMoveNode(self, node, by):
		# get node data
		serialized_data = node.serialize()
		# get current node index
		node_curr_index = self.nodes.index(node)
		# delete node
		self.deleteNode(node)
		# insert node new at index and set data
		self.insertNode(node_curr_index + by).unserialize(serialized_data)

	def onSearch(self, current_text):
		# util functions
		name2Tuple = lambda objectName: (objectName,)
		charFilter = lambda dict_key, tag_filter: set(map(name2Tuple, filter(lambda cName: self.list_view.item(
			self.list_view.all_items[cName]).data(Qt.UserRole)[dict_key] == tag_filter,
			map(lambda t: t[0], founded_items))))
		def clear_combo_box(combo_box):
			while combo_box.count() != 1:
				combo_box.removeItem(1)

		# cascading search starts
		founded_items = set(map(lambda listWidgetItem: (listWidgetItem.text(),),
			self.list_view.findItems(current_text, Qt.MatchContains)))

		db_filter = self.filter_db.currentText()
		if db_filter != "All":
			if len(self.db.execute_query(f"SELECT name FROM sqlite_master WHERE name = '{db_filter}';")) > 0:
				founded_items.intersection_update(set(self.db.execute_query(
					f"SELECT name FROM {db_filter};")))

			elif db_filter == self.list_view.character_tag:
				# all character filter tag; doing the complement to find them
				allItemsTemp: set = set(self.list_view.all_items.keys()) - set(self.list_view.allDialogues)
				all_items = set(map(name2Tuple, allItemsTemp))
				all_items.difference_update(set(self.db.execute_query("SELECT name FROM worldobject;")))
				founded_items.intersection_update(all_items)

			elif db_filter == self.list_view.dialogue_tag:
				founded_items.intersection_update(set(map(name2Tuple, self.list_view.allDialogues)))

			elif db_filter == self.list_view.quest_tag:
				founded_items.intersection_update(set(map(name2Tuple, self.list_view.allQuests)))

		type_filter = self.filter_type.currentText()
		if self.filter_type.isVisible() and type_filter != "All":
			if db_filter == self.list_view.character_tag:
				mapCharacters = charFilter("map", type_filter)
				founded_items.intersection_update(mapCharacters)
				# load only races found in map to sub_type_filter if db == character
				mapRaces = set(map(lambda cTuple:
					self.list_view.item(self.list_view.all_items[cTuple[0]]).data(Qt.UserRole)["race"],
					mapCharacters))
				mapRaces.add("All")
				current_filters = set(map(lambda i: self.filter_sub_type.itemText(i), range(self.filter_sub_type.count())))
				if mapRaces != current_filters:
					clear_combo_box(self.filter_sub_type)
					mapRaces.remove("All")
					mapRaces = list(mapRaces)
					mapRaces.sort()
					self.filter_sub_type.addItems(mapRaces)
			else:
				founded_items.intersection_update(set(self.db.execute_query(
					f"SELECT name FROM worldobject WHERE type LIKE '%{type_filter}%'")))
		elif type_filter == "All" and db_filter == self.list_view.character_tag \
		and self.filter_sub_type.count() < len(self.list_view.sub_type_tags[db_filter]) + 1:
			# reset character filter
			clear_combo_box(self.filter_sub_type)
			self.filter_sub_type.addItems(self.list_view.sub_type_tags[db_filter])

		sub_type_filter = self.filter_sub_type.currentText()
		if self.filter_sub_type.isVisible() and sub_type_filter != "All":
			founded_items.intersection_update(charFilter("race", sub_type_filter))

		founded_items = set([item[0] for item in founded_items])
		for entry in self.list_view.all_items.keys():
			self.list_view.item(self.list_view.all_items[entry]).setHidden(entry not in founded_items)

	def onFilterDb(self, text):
		def clear_combo_box(combo_box):
			while combo_box.count() != 1:
				combo_box.removeItem(1)

		if text in [DataBases.SPELLDB.value.capitalize(), self.list_view.dialogue_tag, self.list_view.quest_tag] \
		or text == "All":
			self.filter_type.hide()
			self.filter_sub_type.hide()
		else:
			clear_combo_box(self.filter_type)
			self.filter_type.addItems(self.list_view.type_tags[self.filter_db.currentText()])
			self.filter_type.show()
			self.filter_sub_type.hide()
			if text == self.list_view.character_tag:
				clear_combo_box(self.filter_sub_type)
				self.filter_sub_type.addItems(self.list_view.sub_type_tags[self.filter_db.currentText()])
				self.filter_sub_type.show()
		self.onSearch(self.search.text())

	def clearWorkspace(self):
		while len(self.nodes) != 0:
			self.deleteNode(self.nodes[0])

	def getFileOpenDialogue(self, save_prompt=False):
		# get last open dir or resort to defaults
		if os.path.isabs(self.current_file):
			self.recent_dir = os.path.dirname(self.current_file)
		elif os.path.isdir(PathManager().get_paths()["content_dir"]):
			self.recent_dir = PathManager().get_paths()["content_dir"]
		else:
			self.recent_dir = QDir().homePath()

		file_filter = "json (*.json)"
		if save_prompt:
			return QFileDialog.getSaveFileName(self, "Save Node File", self.recent_dir, file_filter)[0]
		return QFileDialog.getOpenFileName(self, "Open Node File", self.recent_dir, file_filter)[0]

	def getFileChangeDialogue(self):
		reply = QMessageBox.warning(self, "Unsaved Changes \u2015 %s" % self.title, \
			"There are unsaved changes. Do you want to save now?", \
			QMessageBox.Discard | QMessageBox.Cancel | QMessageBox.Save)
		if reply == QMessageBox.Save:
			self.onSaveFile()
		return reply

	def onNewFile(self):
		if not (self.isModified() \
		and self.getFileChangeDialogue() == QMessageBox.Cancel):
			# bool used to route connection
			app_first_opened = self.node == None
			# ask which kind of work you want to do
			msgBox = QMessageBox(QMessageBox.Question, self.title,
				"Which Node do you want to work on?", parent=self)
			# make buttons
			cancel_bttn = QPushButton('Cancel')
			quest_node_bttn = QPushButton('Quest Node')
			content_node_bttn = QPushButton('Content Node')
			# add buttons
			msgBox.addButton(cancel_bttn, QMessageBox.RejectRole)
			msgBox.addButton(quest_node_bttn, QMessageBox.YesRole)
			msgBox.addButton(content_node_bttn, QMessageBox.NoRole)
			# exec and route reply
			msgBox.exec_()
			if msgBox.clickedButton() == quest_node_bttn:
				self.node = QuestNode
			elif msgBox.clickedButton() == content_node_bttn:
				self.node = CharacterContentNode
			elif msgBox.clickedButton() == cancel_bttn:
				return
			# route (add_node_bttn) signal
			if app_first_opened:
				self.add_node_bttn.clicked.disconnect(self.onNewFile)
				self.add_node_bttn.clicked.connect(self.insertNode)
			# clear work area
			self.clearWorkspace()
			self.clipboard.clearHistoryStack()
			self.current_file = ""
			self.dirty = False
			self.setTitle()
			self.insertNode()

	def onOpenFile(self):
		if not (self.isModified() \
		and self.getFileChangeDialogue() == QMessageBox.Cancel):
			potential_file = self.getFileOpenDialogue()
			if os.path.isabs(potential_file):
				# clear work area
				self.clearWorkspace()
				self.clipboard.clearHistoryStack()
				self.current_file = potential_file
				# load data
				with open(self.current_file, "r") as infile:
					try:
						payload = json.load(infile)
						self.unserialize(payload)
						# make root of history
						self.clipboard.addToHistory(payload)
					except Exception as e:
						print(sys.exc_info())
				# set title
				self.dirty = False
				self.setTitle()

	def onSaveFile(self):
		if os.path.isabs(self.current_file):
			self.setTitle()
			with open(self.current_file, "w") as outfile:
				try:
					json.dump(self.serialize(), outfile, indent="\t")
				except Exception as e:
					print(sys.exc_info())
		else:
			self.onSaveAsFile()

	def onSaveAsFile(self):
		potential_file = self.getFileOpenDialogue(True)
		if os.path.isabs(potential_file):
			# set current file
			self.current_file = potential_file
			# check if user added the appropriate extension
			file_ext = ".json"
			if not self.current_file.endswith(file_ext):
				self.current_file += file_ext
			# save file
			self.onSaveFile()

	def closeEvent(self, QCloseEvent):
		if self.isModified() \
		and self.getFileChangeDialogue() == QMessageBox.Cancel:
			QCloseEvent.ignore()
		else:
			QCloseEvent.accept()

	def onDo(self, redo):
		self.clearWorkspace()
		payload = self.clipboard.redo() if redo else self.clipboard.undo()
		self.unserialize(payload)
		self.disableUndoRedoActions()
		if self.clipboard.isHistoryCurrent():
			# because every single add-in will mark
			# dirty, this is the last saved moment,
			# which means it's not dirty
			self.dirty = False
		self.setTitle()

	def setDirty(self, *args, **kwargs):
		if not self.dirty:
			self.dirty = True
			self.onDirty.trigger()
			self.setTitle()

	def routeDirtiables(self, parent):
		# not implemented, because
		# this node is root
		pass

	def serialize(self):
		payload = OrderedDict([
			("node_type", self.node.__name__),
			("nodes", OrderedDict([
				("node_%d" % i, node.serialize())
				for i, node in enumerate(self.nodes)]))
		])
		if self.dirty:
			# add a stamp of history if changes were made
			# else, it's just a duplicate of history
			self.dirty = False
			self.setTitle()
			self.clipboard.addToHistory(payload)
			self.disableUndoRedoActions()
		return payload

	def unserialize(self, data):
		if self.node == None:
			self.add_node_bttn.clicked.disconnect(self.onNewFile)
			self.add_node_bttn.clicked.connect(self.insertNode)
		self.node = getattr(sys.modules[__name__], data["node_type"])
		for i, node_data in enumerate(data["nodes"]):
			self.insertNode(i).unserialize(data["nodes"][node_data])


if __name__ == "__main__":
	# make app
	app = QApplication(sys.argv)
	ui = MainWindow(app)

	# set style sheet / icon
	rootDir: str = os.path.dirname(__file__)
	path: str = os.path.join(rootDir, "QTDark-master", "QTDark.stylesheet")

	ui.setWindowIcon(QIcon(os.path.join(rootDir, "icon.png")))
	with open(path, "r") as f:
		ui.setStyleSheet(f.read())

	# exec app
	sys.exit(app.exec_())
