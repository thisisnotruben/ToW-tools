#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from types import MethodType
from PyQt5.QtWidgets import QWidget, QListWidgetItem

from gui.quest_maker.views.quest_objective_view import Ui_quest_objective
from gui.quest_maker.ISerializable import ISerializable


class QuestObjective(Ui_quest_objective, QWidget, ISerializable):
    def __init__(self, data={}):
        super().__init__()  
        self.setupUi(self)
        self.show()
        if data:
            self.setData(data)

    def setupUi(self, Form):
        super().setupUi(Form)
        # route list drop event to this class
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
        # only one entry allowed
        self.world_object_drop_event(event)
        if list_widget.count() > 1:
            list_widget.takeItem(0)

    def serialize(self):
        """
        Serialize:
            - World object / Type / Amount
        """
        # TODO
        return super().serialize()

    def unserialize(self, data):
        """
        Unserialize:
            - World object / Type / Amount
        """
        # TODO
        return super().unserialize(data)

