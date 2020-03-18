#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from types import MethodType
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMenu, QAction, QMessageBox
from PyQt5.QtCore import Qt

from gui.quest_maker.views.quest_node_view import Ui_quest_node
from gui.quest_maker.quest_objective import QuestObjective
from gui.quest_maker.ISerializable import ISerializable


class QuestNode(Ui_quest_node, QWidget, ISerializable):
    def __init__(self, db_list):
        super().__init__()
        self.dropEventMap = {}
        self.objectiveEntryMap = {}
        self.db_list = db_list
        self.setupUi(self)
        self.show()
                
    def setupUi(self, quest_node):
        super().setupUi(quest_node)
        self.mapDropEvent(self.giver_list)
        self.mapDropEvent(self.receiver_list)
        self.addObjective()
        # setup delete button function
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.delete_node_bttn.clicked.connect(self.onDeleteSelf)
        
    def onDeleteSelf(self):
        reply = QMessageBox.question(self, "Delete Quest Node",
            "Delete?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.hide()

    def contextMenuEvent(self, QContextMenuEvent):
        # only allow one empty objective entry in list
        for row in range(self.objective_list.count()):
            if self.getObjective(row).isEmpty():
                super().contextMenuEvent(QContextMenuEvent)
                return
        # create context menu
        menu = QMenu(self)
        # create actions
        add_action = QAction("Add", triggered=self.addObjective)
        menu.addAction(add_action)
        # exec action
        action = menu.exec_(QContextMenuEvent.globalPos())

    def objectiveContextMenu(self, objective_node, QContextMenuEvent):
        # get index from right click
        row = self.objective_list.row(self.objectiveEntryMap[objective_node])
        objective = self.getObjective(row)
        next_objective = self.getObjective(row + 1)
        # create context menu
        menu = QMenu(self)
        # create actions
        move_up_action = QAction("Move Up",
            triggered=lambda: self.move(row, -1))
        move_down_action = QAction("Move Down",
            triggered=lambda: self.move(row, 1))
        delete_action = QAction("Delete",
            triggered=lambda: self.delete(row))
        # set actions according to index
        if not objective.isEmpty():
            if row > 0:
                menu.addSeparator()
                menu.addAction(move_up_action)
            if next_objective != None and not next_objective.isEmpty():
                menu.addAction(move_down_action)
        if row > 0:
            menu.addSeparator()
            menu.addAction(delete_action)
        # exec action
        action = menu.exec_(QContextMenuEvent.globalPos())

    def delete(self, row):
        objective = self.getObjective(row)
        # delete entry
        self.objective_list.takeItem(row)
        # delete events from objective copied
        self.objectiveEntryMap.pop(objective)
    
    def move(self, row, by):
        # get widgets
        objective = self.copyObjective(row, self.objective_list.item(row))
        entry = self.objective_list.takeItem(row)
        # move widgets
        self.objective_list.insertItem(row + by, entry)
        self.objective_list.setItemWidget(entry, objective)

    def copyObjective(self, row, entry):
        # transfer data
        objective = self.getObjective(row)
        copied_objective = QuestObjective(objective.getData())
        # route events to objective copied
        self.routeObjectiveContextMenu(copied_objective, entry)
        # delete events from objective copied
        self.objectiveEntryMap.pop(objective)
        # return copied object
        return copied_objective

    def getObjective(self, row):
        entry = self.objective_list.item(row)
        return None if entry == None else self.objective_list.itemWidget(entry)

    def addObjective(self):
        # init widgets to add
        objective = QuestObjective()
        entry = QListWidgetItem(self.objective_list)
        entry.setSizeHint(objective.minimumSizeHint())
        # route objective events
        self.routeObjectiveContextMenu(objective, entry)
        # insert widgets
        self.objective_list.addItem(entry)
        self.objective_list.setItemWidget(entry, objective)

    def routeObjectiveContextMenu(self, objective, entry):
        objective.contextMenuEvent = MethodType(self.objectiveContextMenu, objective)
        self.objectiveEntryMap[objective] = entry

    def mapDropEvent(self, list_widget):
        self.dropEventMap[list_widget] = list_widget.dropEvent
        list_widget.dropEvent = MethodType(self.onDropEvent, list_widget)

    def onDropEvent(self, list_widget, event):
        self.dropEventMap[list_widget](event)
        row = list_widget.count() - 1
        character_entry = list_widget.item(row)
        # Only allow one entry, and can only be characters
        if not self.db_list.isCharacter(character_entry.text()):
            list_widget.takeItem(row)
        elif list_widget.count() > 1:
            list_widget.takeItem(row - 1)

    def serialize(self):
        """
        Serialize:
            - Quest name
            - Quest Giver
            - Quest Receiver
            - Dialogues for Giver/Receiver
            - Objectives
        """
        # TODO
        return super().serialize()

    def unserialize(self, data):
        """
        Unserialize:
            - Quest name
            - Quest Giver
            - Quest Receiver
            - Dialogues for Giver/Receiver
            - Objectives
        """
        # TODO
        return super().unserialize(data)

