#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from types import MethodType
from PyQt5.QtWidgets import QWidget, QListWidgetItem

from gui.quest_maker.views.quest_objective_view import Ui_quest_objective
from gui.quest_maker.ISerializable import ISerializable, OrderedDict
from gui.quest_maker.icon_generator import IconGenerator


class QuestObjective(Ui_quest_objective, QWidget, ISerializable):
    def __init__(self, db_list, data={}):
        super().__init__()  
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

    def serialize(self):
        """
        Serialize:
            - World object / Type / Amount
        """
        payload = OrderedDict([
            ("world_object", ""),
            ("world_object_icon", -1),
            ("quest_type", self.quest_type.currentText()),
            ("amount", self.amount.value())
        ])
        world_object = self.world_object.item(0)
        if world_object != None:
            payload["world_object"] = world_object.text()
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
            self.quest_type.setCurrentText(data["quest_type"])
        # set amount
        self.amount.setValue(int(data["amount"]))

