#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

import os
import sys
import json
from PyQt5.QtWidgets import QApplication, QMessageBox, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

root_dir = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir)
sys.path.insert(0, root_dir)

from gui.quest_maker.views.quest_main_view import Ui_quest_maker_main
from gui.quest_maker.game_database import DataView
from gui.quest_maker.quest_node import QuestNode
from gui.quest_maker.ISerializable import ISerializable, OrderedDict

from core.game_db import DataBases


class MainWindow(Ui_quest_maker_main, QMainWindow, ISerializable):
    def __init__(self):
        super().__init__()
        self.quest_nodes = []
        self.title = "Tides of War Quest Maker"
        self.about = "Author: Ruben Alvarez Reyes<br/>Source: " \
            "<a href=\"https://github.com/thisisnotruben/ToW-tools/\">Github</a>"
        self.setupUi(self)
        self.showMaximized()
    
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        # set main window title/icon
        icon = QIcon(os.path.join(root_dir, "icon.png"))
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowTitle(self.title)
        # route save action
        # TODO: needs to be implemented more robustly
        self.action_save.triggered.connect(self.serialize)
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
        self.add_quest_node_bttn.clicked.connect(self.addQuestNode)
        # add quest node so there is no empty screen
        self.addQuestNode()    

    def addQuestNode(self):
        node = QuestNode(self.list_view)
        node.delete_node_bttn.clicked.connect(lambda: self.quest_nodes.remove(node))
        self.scroll_layout.insertWidget(0, node)
        self.quest_nodes.append(node)
        return node
        
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

    def serialize(self):
        """
        Serialize:
            - Quest Nodes
        """
        payload = OrderedDict([
            ("quest_node_%d" % i, node.serialize())
                for i, node in enumerate(self.quest_nodes)])
        # TODO: this operation below must be moved to another function
        with open(os.path.join(root_dir, "TEST.json"), "w") as outfile:
            json.dump(payload, outfile, indent=4)
        return payload

    def unserialize(self, data):
        """
        Unserialize:
            - Quest Nodes
        """
        for quest_node_data in data:
            self.addQuestNode().unserialize(quest_node_data)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindow()
    sys.exit(app.exec_())
