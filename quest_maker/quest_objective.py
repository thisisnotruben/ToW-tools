#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from types import MethodType
from collections import OrderedDict
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QAction, QMessageBox

from quest_maker.views.quest_objective_view import Ui_quest_objective
from quest_maker.metas import ISerializable, Dirty
from quest_maker.icon_generator import IconGenerator


class QuestObjective(Ui_quest_objective, QWidget, ISerializable, Dirty):
    def __init__(self, db_list, data={}):
        super().__init__()
        Dirty.__init__(self)
        self.db_list = db_list
        self.setupUi(self)
        self.show()

    def setupUi(self, Form):
        super().setupUi(Form)
        # route list drop event to this class
        self.world_object_drop_event = self.world_object.dropEvent
        self.world_object.dropEvent = MethodType(self.onDropEvent, self.world_object)

    def isEmpty(self):
        return self.world_object.count() == 0

    def onDropEvent(self, list_widget, event):
        # only one entry allowed
        self.world_object_drop_event(event)
        if list_widget.count() > 1:
            list_widget.takeItem(0)
        # if character name is not unique ask if you want this character
        # in particular, or all units with this name
        entry_name = self.getWorldObjectName()
        if not self.db_list.isEntryUnique(entry_name):            
            reply = QMessageBox.question(self, "Duplicate found in world \u2015 Tides of War", \
                "World object is mentioned more then once in game. "
                "Include all world objects with this name, or just "
                "this specific world object?",
                QMessageBox.YesToAll | QMessageBox.Yes | QMessageBox.Cancel)
            # route reply
            if reply == QMessageBox.Yes:
                # since it's unique, there can only
                # an amount of one
                self.amount.setValue(1)
                self.amount.setDisabled(True)
            elif reply == QMessageBox.YesToAll:
                entry = self.world_object.item(0)
                entry.setText(self.db_list.getEntryNameToGameName(entry.text()))
            elif reply == QMessageBox.Cancel:
                self.onObjectveDelete(self.objective_list.count() - 1)
        # spells and unique characters can only have an amount one
        elif self.db_list.isSpell(entry_name) \
        or (self.db_list.isCharacter(entry_name) \
        and self.db_list.isEntryUnique(entry_name)):
            self.amount.setValue(1)
            self.amount.setDisabled(True)
        # set quest types in combo box
        while self.quest_type.count() != 0:
            self.quest_type.removeItem(0)
        self.quest_type.addItems(
            [
                tag.capitalize()
                for tag in self.db_list.getQuestTypeTags(entry_name)
            ]
        )
    
    def routeDirtiables(self, parent):
        self.onDirty = QAction(triggered=lambda: parent.setDirty([]))
        self.world_object.itemChanged.connect(parent.setDirty)
        self.quest_type.currentTextChanged.connect(parent.setDirty)
        self.amount.valueChanged.connect(parent.setDirty)

    def getWorldObjectName(self):
        world_object = self.world_object.item(0)
        return world_object.text() if world_object != None else ""

    def serialize(self):
        """
        Serialize:
            - World object / Type / Amount
        """
        self.dirty = False
        payload = OrderedDict([
            ("world_object", self.getWorldObjectName()),
            ("world_object_icon", -1),
            ("quest_type", self.quest_type.currentText().lower()),
            ("amount", self.amount.value())
        ])
        if payload["world_object"] != "":
            payload["world_object_icon"] = \
            self.db_list.getEntryIconSource(payload["world_object"])
        return payload

    def unserialize(self, data):
        """
        Unserialize:
            - World object / Type / Amount
        """
        # set world object
        if data["world_object"] != "":
            icon = IconGenerator().getIcon(data["world_object_icon"])
            self.world_object.addItem(QListWidgetItem(icon, data["world_object"]))
        # set quest type
        if data["quest_type"] != "":
            self.quest_type.addItems(
                [
                    tag.capitalize()
                    for tag in self.db_list.getQuestTypeTags(data["world_object"])
                ]
            )
        self.quest_type.setCurrentText(data["quest_type"].capitalize())
        # set amount
        self.amount.setValue(int(data["amount"]))

