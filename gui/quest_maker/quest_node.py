#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from types import MethodType
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMenu, QAction, QMessageBox
from PyQt5.QtCore import Qt

from gui.quest_maker.views.quest_node_view import Ui_quest_node
from gui.quest_maker.quest_objective import QuestObjective
from gui.quest_maker.ISerializable import ISerializable, OrderedDict
from gui.quest_maker.icon_generator import IconGenerator


class QuestNode(Ui_quest_node, QWidget, ISerializable):
    def __init__(self, db_list):
        super().__init__()
        self.dropEventMap = {}
        self.objectiveEntryMap = OrderedDict()
        self.db_list = db_list
        self.setupUi(self)
        self.show()
                
    def setupUi(self, quest_node):
        super().setupUi(quest_node)
        # map character lists drop events
        for list_widget in [self.giver_list, self.receiver_list]:
            self.dropEventMap[list_widget] = list_widget.dropEvent
            list_widget.dropEvent = MethodType(self.onCharacterDropEvent, list_widget)
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
            menu.addSeparator()
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
        entry = QListWidgetItem(self.objective_list)
        entry.setSizeHint(objective.minimumSizeHint())
        # route objective events
        self.routeObjectiveContextMenu(objective, entry)
        # insert widgets
        self.objective_list.addItem(entry)
        self.objective_list.setItemWidget(entry, objective)
        return objective

    def serialize(self):
        """
        Serialize:
            - Quest name
            - Quest Giver
            - Quest Receiver
            - Dialogues for Giver/Receiver
            - Objectives
        """
        payload = OrderedDict([
            ("quest_name", self.name_entry.text()),
            ("quest_giver", ""),
            ("quest_giver_icon", -1),
            ("quest_receiver", ""),
            ("quest_receiver_icon", -1)
        ])
        quest_giver = self.giver_list.item(0)
        quest_receiver = self.receiver_list.item(0)
        if quest_giver != None:
            payload["quest_giver"] = quest_giver.text()
            payload["quest_giver_icon"] = \
                self.db_list.getEntryIconSource(payload["quest_giver"])
        if quest_receiver != None:
            payload["quest_receiver"] = quest_receiver.text()
            payload["quest_receiver_icon"] = \
                self.db_list.getEntryIconSource(payload["quest_receiver"])

        giver_dialogue = OrderedDict([
            ("start", self.g_start_entry.toPlainText()),
            ("active", self.g_active_entry.toPlainText()),
            ("completed", self.g_completed_entry.toPlainText()),
            ("delivered", self.g_delivered_entry.toPlainText())
        ])

        receiver_dialogue = OrderedDict([
            ("start", self.r_start_entry.toPlainText()),
            ("active", self.r_active_entry.toPlainText()),
            ("completed", self.r_completed_entry.toPlainText()),
            ("delivered", self.r_delivered_entry.toPlainText())
        ])

        objective_data = OrderedDict([
            ("objective_%d" % i, objective.serialize())
                for i, objective in enumerate(self.objectiveEntryMap.keys())
        ])
        
        payload["giver_dialogue"] = giver_dialogue
        payload["receiver_dialogue"] = receiver_dialogue
        payload["objectives"] = objective_data
        return payload

    def unserialize(self, data):
        """
        Unserialize:
            - Quest name
            - Quest Giver
            - Quest Receiver
            - Dialogues for Giver/Receiver
            - Objectives
        """
        icon_generator = IconGenerator()
        # set quest name
        self.name_entry.setText(data["quest_name"])
        # set quest giver
        if data["quest_giver"] != "":
            icon = icon_generator.getIcon(data["quest_giver_icon"])
            self.giver_list.addItem(QListWidgetItem(icon, data["quest_giver"]))
        # set quest reciever
        if data["quest_receiver"] != "":
            icon = icon_generator.getIcon(data["quest_receiver_icon"])
            self.receiver_list.addItem(QListWidgetItem(icon, data["quest_receiver"]))
        # set quest giver dialogues
        self.g_start_entry.setText(data["giver_dialogue"]["start"])
        self.g_active_entry.setText(data["giver_dialogue"]["active"])
        self.g_completed_entry.setText(data["giver_dialogue"]["completed"])
        self.g_delivered_entry.setText(data["giver_dialogue"]["delivered"])
        # set quest reciever dialogues
        self.r_start_entry.setText(data["receiver_dialogue"]["start"])
        self.r_active_entry.setText(data["receiver_dialogue"]["active"])
        self.r_completed_entry.setText(data["receiver_dialogue"]["completed"])
        self.r_delivered_entry.setText(data["receiver_dialogue"]["delivered"])
        # set quest objectives
        for objective_data in data["objectives"].keys():
            self.addObjective().unserialize(data["objectives"][objective_data])

