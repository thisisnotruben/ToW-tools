#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from types import MethodType
from collections import OrderedDict
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMenu, QAction, QMessageBox
from PyQt5.QtCore import Qt

from content_maker.views.quest_node_view import Ui_quest_node_view
from content_maker.quest_objective import QuestObjective
from content_maker.metas import ISerializable, Dirty
from content_maker.icon_generator import IconGenerator


class QuestNode(Ui_quest_node_view, QWidget, ISerializable, Dirty):
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
        self.reward_list.contextMenuEvent = MethodType(self.onListContextMenu, self.reward_list)
        self.reward_list.itemChanged.connect(self.onRewardListItemChanged)
        self.next_quest_list.contextMenuEvent = MethodType(self.onListContextMenu, self.next_quest_list)
        self.next_quest_list.setDisabled(True) # TODO: need to setup database first to support this drop
        for list_widget in [self.giver_list, self.completer_list]:
            self.dropEventMap[list_widget] = list_widget.dropEvent
            list_widget.dropEvent = MethodType(self.onCharacterDropEvent, list_widget)
            list_widget.contextMenuEvent = MethodType(self.onListContextMenu, list_widget)
        # setup delete button function
        self.delete_node_bttn.clicked.connect(self.deleteNode)
        self.on_delete_confirm = QAction()
        # map objective list drop events
        self.objective_list.dropEvent = MethodType(
            self.onObjectiveListDropEvent, self.objective_list)

    def onRewardListItemChanged(self, listWidgetItem):
        # no characters allowed
        if self.db_list.isCharacter(listWidgetItem.text()):
            self.reward_list.takeItem(self.reward_list.count() - 1)

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
        if hasattr(objective, "delete_self"):
            # when the user clicks on cancel
            self.onObjectveDelete(self.objective_list.count() - 1)

    def copyObjective(self, row, entry):
        # transfer data
        objective = self.getObjective(row)
        copied_objective = QuestObjective(self, self.db_list)
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
        objective = QuestObjective(self, self.db_list)
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
        self.next_quest_list.itemChanged.connect(parent.setDirty)
        self.reward_list.itemChanged.connect(parent.setDirty)
        self.reward_keep.stateChanged.connect(parent.setDirty)
        self.gold_reward_amount.valueChanged.connect(parent.setDirty)
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
        self.dirty = False

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
            ("questName", self.name_entry.text()),
            ("nextQuest", getItemData(self.next_quest_list)),
            ("reward", getItemData(self.reward_list)),
            ("keepRewardItems", self.reward_keep.isChecked()),
            ("goldReward", self.gold_reward_amount.value()),
            ("questGiver", getItemData(self.giver_list, True)),
            ("questCompleter", getItemData(self.completer_list, True)),
            ("available", self.start_entry.toPlainText()),
            ("active", self.active_entry.toPlainText()),
            ("completed", self.completed_entry.toPlainText()),
            ("delivered", self.delivered_entry.toPlainText())
        ])

        objective_data = OrderedDict([
            ("objective_%d" % i, objective.serialize())
                for i, objective in enumerate(self.objectiveEntryMap.keys())
        ])

        payload["objectives"] = objective_data
        return payload

    def unserialize(self, data):
        icon_generator = IconGenerator()
        def unpackItemData(list_widget, serialized_list_data):
            icon = icon_generator.getIcon(serialized_list_data[1])
            list_widget.addItem(QListWidgetItem(icon, serialized_list_data[0]))

        # set quest name
        self.name_entry.setText(data["questName"])
        # set next quest
        for quest in data["nextQuest"]:
            unpackItemData(self.next_quest_list, quest)
        # set rewards
        for reward in data["reward"]:
            unpackItemData(self.reward_list, reward)
        # set keep reward items
        self.reward_keep.setChecked(bool(data["keepRewardItems"]))
        # set gold reward
        self.gold_reward_amount.setValue(int(data["goldReward"]))
        # set quest giver
        if len(data["questGiver"]) != 0:
            unpackItemData(self.giver_list, data["questGiver"])
        # set quest completer
        if len(data["questCompleter"]) != 0:
            unpackItemData(self.completer_list, data["questCompleter"])
        # set quest giver dialogues
        self.start_entry.setText(data["available"])
        self.active_entry.setText(data["active"])
        self.completed_entry.setText(data["completed"])
        self.delivered_entry.setText(data["delivered"])
        # set quest objectives
        for objective_data in data["objectives"].keys():
            self.addObjective().unserialize(data["objectives"][objective_data])

