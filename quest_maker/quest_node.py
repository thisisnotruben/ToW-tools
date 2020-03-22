#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from types import MethodType
from collections import OrderedDict
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMenu, QAction, QMessageBox
from PyQt5.QtCore import Qt

from quest_maker.views.quest_node_view import Ui_quest_node
from quest_maker.quest_objective import QuestObjective
from quest_maker.metas import ISerializable, Dirty
from quest_maker.icon_generator import IconGenerator


class QuestNode(Ui_quest_node, QWidget, ISerializable, Dirty):
    def __init__(self, db_list):
        super().__init__()
        Dirty.__init__(self)
        self.dropEventMap = {}
        self.objectiveEntryMap = OrderedDict()
        self.db_list = db_list
        self.setupUi(self)
        self.show()
                
    def setupUi(self, quest_node):
        super().setupUi(quest_node)
        # map character lists drop events and contxt menus
        for list_widget in [self.giver_list, self.completer_list]:
            self.dropEventMap[list_widget] = list_widget.dropEvent
            list_widget.dropEvent = MethodType(self.onCharacterDropEvent, list_widget)
            list_widget.contextMenuEvent = MethodType(self.onListContextMenu, list_widget)
        # setup delete button function
        self.delete_node_bttn.clicked.connect(self.deleteQuestNode)
        self.on_delete_confirm = QAction()
        # map objective list drop events
        self.objective_list.dropEvent = MethodType(
            self.onObjectiveListDropEvent, self.objective_list)

    def onCharacterDropEvent(self, list_widget, event):
        self.dropEventMap[list_widget](event)
        row = list_widget.count() - 1
        character_entry = list_widget.item(row)
        # Only allow one entry, and can only be characters
        if not self.db_list.isCharacter(character_entry.text()):
            list_widget.takeItem(row)
        elif list_widget.count() > 1:
            list_widget.takeItem(row - 1)

    def onListContextMenu(self, list_widget, QContextMenuEvent):
        # get select item
        row = list_widget.indexAt(QContextMenuEvent.pos()).row()
        # create context menu
        menu = QMenu(self)
        # create actions
        delete_action = QAction("Delete",
            triggered=lambda: list_widget.takeItem(row))
        menu.addAction(delete_action)
        # exec actionrow
        action = menu.exec_(QContextMenuEvent.globalPos())

    def deleteQuestNode(self, bypass_prompt=False):
        self.setAttribute(Qt.WA_DeleteOnClose)
        if bypass_prompt:
            self.on_delete_confirm.trigger()
            self.close()
        else:
            reply = QMessageBox.question(self, "Delete Quest Node",
                "Delete?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.on_delete_confirm.trigger()
                self.close()
    
    def routeObjectiveContextMenu(self, objective, entry):
        objective.contextMenuEvent = MethodType(self.onObjectiveContextMenu, objective)
        self.objectiveEntryMap[objective] = entry
        
    def onObjectiveContextMenu(self, objective_node, QContextMenuEvent):
        # get index from right click
        row = self.objective_list.row(self.objectiveEntryMap[objective_node])
        objective = self.getObjective(row)
        next_objective = self.getObjective(row + 1)
        # create context menu
        menu = QMenu(self)
        # create actions
        move_up_action = QAction("Move Up",
            triggered=lambda: self.onObjectveMove(row, -1))
        move_down_action = QAction("Move Down",
            triggered=lambda: self.onObjectveMove(row, 1))
        delete_action = QAction("Delete",
            triggered=lambda: self.onObjectveDelete(row))
        # set actions according to index
        if row > 0:
            menu.addAction(move_up_action)
        if next_objective != None and not next_objective.isEmpty():
            menu.addAction(move_down_action)
        menu.addSeparator()
        menu.addAction(delete_action)
        # exec action
        action = menu.exec_(QContextMenuEvent.globalPos())

    def onObjectveDelete(self, row):
        objective = self.getObjective(row)
        # delete entry
        self.objective_list.takeItem(row)
        # delete events from objective copied
        self.objectiveEntryMap.pop(objective)
    
    def onObjectveMove(self, row, by):
        # get widgets
        objective = self.copyObjective(row, self.objective_list.item(row))
        entry = self.objective_list.takeItem(row)
        # move widgets
        self.objective_list.insertItem(row + by, entry)
        self.objective_list.setItemWidget(entry, objective)

    def onObjectiveListDropEvent(self, list_widget, QDropEvent):
        # create quest objective on drop
        objective = self.addObjective()
        objective.onDropEvent(objective.world_object, QDropEvent)
        # check if dropped event is a duplicate and delete if it is
        for other_objective in self.objectiveEntryMap.keys():
            if other_objective.getWorldObjectName() == objective.getWorldObjectName() \
            and other_objective != objective:
                self.onObjectveDelete(self.objective_list.count() - 1)
                break

    def copyObjective(self, row, entry):
        # transfer data
        objective = self.getObjective(row)
        copied_objective = QuestObjective(self.db_list)
        copied_objective.unserialize(objective.serialize())
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
        objective = QuestObjective(self.db_list)
        objective.routeDirtiables(self)
        entry = QListWidgetItem(self.objective_list)
        entry.setSizeHint(objective.minimumSizeHint())
        # route objective events
        self.routeObjectiveContextMenu(objective, entry)
        # insert widgets
        self.objective_list.addItem(entry)
        self.objective_list.setItemWidget(entry, objective)
        return objective

    def routeDirtiables(self, parent):
        self.onDirty = QAction(triggered=lambda: parent.setDirty([]))
        self.move_node_left_bttn.clicked.connect(parent.setDirty)
        self.move_node_right_bttn.clicked.connect(parent.setDirty)

        self.name_entry.textChanged.connect(parent.setDirty)
        self.giver_list.itemChanged.connect(parent.setDirty)
        self.completer_list.itemChanged.connect(parent.setDirty)

        dialogue_entries = [
            self.start_entry,
            self.active_entry,
            self.completed_entry,
            self.delivered_entry
        ]
        for entry in dialogue_entries:
            entry.textChanged.connect(parent.setDirty)

    def serialize(self):
        """
        Serialize:
            - Quest name
            - Quest Giver
            - Quest Completer
            - Dialogues for Quest Giver
            - Objectives
        """
        self.dirty = False
        payload = OrderedDict([
            ("quest_name", self.name_entry.text()),
            ("quest_giver", ""),
            ("quest_giver_icon", -1),
            ("quest_completer", ""),
            ("quest_completer_icon", -1)
        ])
        quest_giver = self.giver_list.item(0)
        quest_completer = self.completer_list.item(0)
        if quest_giver != None:
            payload["quest_giver"] = quest_giver.text()
            payload["quest_giver_icon"] = \
                self.db_list.getEntryIconSource(payload["quest_giver"])
        if quest_completer != None:
            payload["quest_completer"] = quest_completer.text()
            payload["quest_completer_icon"] = \
                self.db_list.getEntryIconSource(payload["quest_completer"])

        giver_dialogue = OrderedDict([
            ("start", self.start_entry.toPlainText()),
            ("active", self.active_entry.toPlainText()),
            ("completed", self.completed_entry.toPlainText()),
            ("delivered", self.delivered_entry.toPlainText())
        ])

        objective_data = OrderedDict([
            ("objective_%d" % i, objective.serialize())
                for i, objective in enumerate(self.objectiveEntryMap.keys())
        ])
        
        payload["giver_dialogue"] = giver_dialogue
        payload["objectives"] = objective_data
        return payload

    def unserialize(self, data):
        """
        Unserialize:
            - Quest name
            - Quest Giver
            - Quest Completer
            - Dialogues for Quest Giver
            - Objectives
        """
        icon_generator = IconGenerator()
        # set quest name
        self.name_entry.setText(data["quest_name"])
        # set quest giver
        if data["quest_giver"] != "":
            icon = icon_generator.getIcon(data["quest_giver_icon"])
            self.giver_list.addItem(QListWidgetItem(icon, data["quest_giver"]))
        # set quest completer
        if data["quest_completer"] != "":
            icon = icon_generator.getIcon(data["quest_completer_icon"])
            self.completer_list.addItem(QListWidgetItem(icon, data["quest_completer"]))
        # set quest giver dialogues
        self.start_entry.setText(data["giver_dialogue"]["start"])
        self.active_entry.setText(data["giver_dialogue"]["active"])
        self.completed_entry.setText(data["giver_dialogue"]["completed"])
        self.delivered_entry.setText(data["giver_dialogue"]["delivered"])
        # set quest objectives
        for objective_data in data["objectives"].keys():
            self.addObjective().unserialize(data["objectives"][objective_data])

