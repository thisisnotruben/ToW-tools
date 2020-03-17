#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from types import MethodType
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMenu, QAction
from PyQt5.QtCore import Qt

from gui.quest_maker.views.gui_quest_node import Ui_quest_node
from gui.quest_maker.views.gui_quest_objective import Ui_Form


class QuestObjective(Ui_Form, QWidget):
    def __init__(self, data={}):
        super().__init__()  
        self.setupUi(self)
        self.show()
        if data:
            self.setData(data)

    def setupUi(self, Form):
        super().setupUi(Form)
        self.world_object_drop_event = self.world_object.dropEvent
        self.world_object.dropEvent = MethodType(self.onDropEvent, self.world_object)

    def getData(self):
        data = {}
        world_object = self.world_object.item(0)
        data["item_name"] = world_object.text()
        data["item_icon"] = world_object.icon()
        data["amount"] = self.amount.value()
        # TODO
        # data["quest_types"] = self.quest_type.currentText()
        return data

    def setData(self, data):
        world_object = QListWidgetItem(data["item_icon"], data["item_name"])
        self.world_object.addItem(world_object)
        # TODO
        # self.quest_type
        self.amount.setValue(data["amount"])

    def isEmpty(self):
        return self.world_object.count() == 0

    def onDropEvent(self, list_widget, event):
        self.world_object_drop_event(event)
        if list_widget.count() > 1:
            list_widget.takeItem(0)

class QuestNode(Ui_quest_node, QWidget):

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
        self.routeObjectiveSignals(copied_objective, entry)
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
        self.routeObjectiveSignals(objective, entry)
        # insert widgets
        self.objective_list.addItem(entry)
        self.objective_list.setItemWidget(entry, objective)

    def routeObjectiveSignals(self, objective, entry):
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

