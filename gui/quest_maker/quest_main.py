#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import os
import sys
import json
from collections import OrderedDict
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow, QAction, QFileDialog
from PyQt5.QtGui import QIcon, QCloseEvent
from PyQt5.QtCore import Qt, QDir

root_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
sys.path.insert(0, root_dir)

from gui.quest_maker.views.quest_main_view import Ui_quest_maker_main
from gui.quest_maker.game_database import DataView
from gui.quest_maker.quest_node import QuestNode
from gui.quest_maker.metas import ISerializable, Dirty
from gui.quest_maker.clipboard import Clipboard

from core.game_db import DataBases


class MainWindow(Ui_quest_maker_main, QMainWindow, ISerializable, Dirty):
    def __init__(self, app):
        super().__init__()
        Dirty.__init__(self)

        self.clipboard = Clipboard()
        self.quest_nodes = []
        self.current_file = ""

        self.title = "Tides of War Quest Maker"
        self.about = "Author: Ruben Alvarez Reyes<br/>Source: " \
            "<a href=\"https://github.com/thisisnotruben/ToW-tools/\">Github</a>"

        self.app = app
        self.setupUi(self)
        self.showMaximized()
    
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        # set main window title/icon
        icon = QIcon(os.path.join(root_dir, "icon.png"))
        MainWindow.setWindowIcon(icon)
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
        self.add_quest_node_bttn.clicked.connect(self.insertQuestNode)

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

    def insertQuestNode(self, index=0):
        self.setDirty([])
        # init widget 
        node = QuestNode(self.list_view)
        node.routeDirtiables(self)
        # route button connections
        node.on_delete_confirm = QAction(
            triggered=lambda: self.onDeleteQuestNodeConfirm(node))
        node.move_node_left_bttn.clicked.connect(
            lambda: self.onMoveQuestNode(node, -1))
        node.move_node_right_bttn.clicked.connect(
            lambda: self.onMoveQuestNode(node, 1))
        # add widget
        self.scroll_layout.insertWidget(index, node)
        self.quest_nodes.insert(index, node)
        # name all quest node headers
        for i, n in enumerate(self.quest_nodes):
            n.group_box.setTitle("Quest Node %d" % i)
        # possibly disable move buttons
        # for node and neighbor nodes
        self.disableQuestNodeMoveButtons(index)
        self.disableQuestNodeMoveButtons(index - 1)
        self.disableQuestNodeMoveButtons(index + 1)
        return node

    def deleteQuestNode(self, quest_node):
        quest_node.deleteQuestNode(True)

    def disableUndoRedoActions(self):
        # check index of buttons and 
        # potentially disable buttons
        reached_end = self.clipboard.reached_end()
        self.action_undo.setDisabled(reached_end[0])
        self.action_redo.setDisabled(reached_end[1])
        self.undo_save_bttn.setDisabled(reached_end[0])
        self.redo_save_bttn.setDisabled(reached_end[1])

    def disableQuestNodeMoveButtons(self, index):
        # disable move left/right buttons based on first/last index
        if index >= 0 and index < len(self.quest_nodes):
            self.quest_nodes[index].move_node_left_bttn.setDisabled( \
                index == 0)
            self.quest_nodes[index].move_node_right_bttn.setDisabled( \
                index == len(self.quest_nodes) - 1)

    def onDeleteQuestNodeConfirm(self, quest_node):
        self.setDirty([])
        index = self.quest_nodes.index(quest_node)
        self.quest_nodes.remove(quest_node)
        self.scroll_layout.removeWidget(quest_node)
        # possibly disable move buttons
        # for node and neighbor nodes
        self.disableQuestNodeMoveButtons(index)
        self.disableQuestNodeMoveButtons(index - 1)
        self.disableQuestNodeMoveButtons(index + 1)

    def onMoveQuestNode(self, quest_node, by):
        # get node data
        serialized_data = quest_node.serialize()
        # get current node index
        node_curr_index = self.quest_nodes.index(quest_node)
        # delete node
        self.deleteQuestNode(quest_node)
        # insert node new at index and set data
        self.insertQuestNode(node_curr_index + by).unserialize(serialized_data)
  
    def onSearch(self, current_text):
        founded_items = set(self.list_view.findItems(current_text, Qt.MatchContains))

        db_filter = self.filter_db.currentText()
        if db_filter != "All":
            founded_items = set([entry for entry in founded_items
                if entry.data(Qt.UserRole)["_DB"] == db_filter])

        type_filter = self.filter_type.currentText()
        if self.filter_type.isVisible() and type_filter != "All":
            founded_items = set([entry for entry in founded_items
                if entry.data(Qt.UserRole)["_TYPE"].capitalize() == type_filter])
        
        sub_type_filter = self.filter_sub_type.currentText()
        if self.filter_sub_type.isVisible() and sub_type_filter != "All":
            founded_items = set([entry for entry in founded_items
                if "_SUB_TYPE" in entry.data(Qt.UserRole)
                and entry.data(Qt.UserRole)["_SUB_TYPE"] == sub_type_filter])
        
        for entry in founded_items:
            entry.setHidden(False)
        for entry in self.list_view.all_items - founded_items:
            entry.setHidden(True)

    def onFilterDb(self, text):
        def clear_combo_box(combo_box):
            while combo_box.count() != 1:
                combo_box.removeItem(1)

        if text == DataBases.SPELLDB.value or text == "All":
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
        while len(self.quest_nodes) != 0:
            self.deleteQuestNode(self.quest_nodes[0])

    def getFileOpenDialogue(self, save_prompt=False):
        self.recent_dir = os.path.dirname(self.current_file) \
            if os.path.isabs(self.current_file) else QDir().homePath()
        file_filter = "json (*.json)"
        if save_prompt:
            return QFileDialog.getSaveFileName(self, "Save Quest File", self.recent_dir, file_filter)[0]
        return QFileDialog.getOpenFileName(self, "Open Quest File", self.recent_dir, file_filter)[0]

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
            # clear work area
            self.clearWorkspace()
            self.clipboard.clearHistoryStack()
            self.current_file = ""
            self.dirty = False
            self.setTitle()

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
                    json.dump(self.serialize(), outfile, indent=4)
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
        """
        Serialize:
            - Quest Nodes
        """
        payload = OrderedDict([
            ("quest_node_%d" % i, node.serialize())
                for i, node in enumerate(self.quest_nodes)])
        if self.dirty:
            # add a stamp of history if changes were made
            # else, it's just a duplicate of history
            self.dirty = False
            self.setTitle()
            self.clipboard.addToHistory(payload)
            self.disableUndoRedoActions()
        return payload

    def unserialize(self, data):
        """
        Unserialize:
            - Quest Nodes
        """
        for i, quest_node_data in enumerate(data):
            self.insertQuestNode(i).unserialize(data[quest_node_data])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindow(app)
    sys.exit(app.exec_())
