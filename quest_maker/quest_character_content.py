#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from types import MethodType
from collections import OrderedDict
from PyQt5.QtWidgets import QAction, QListWidgetItem, QWidget, QMenu
from PyQt5.QtCore import Qt

from quest_maker.views.quest_character_content_view import Ui_quest_character_content
from quest_maker.metas import ISerializable, Dirty
from quest_maker.icon_generator import IconGenerator


class QuestCharacterContent(Ui_quest_character_content, QWidget, ISerializable, Dirty):
    def __init__(self, db_list):
        super().__init__()
        Dirty.__init__(self)
        self.db_list = db_list
        self.setupUi(self)

    def setupUi(self, quest_character_content):
        super().setupUi(quest_character_content)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        # route context menu & drop events
        self.reward.itemChanged.connect(self.onRewardItemChanged)
        self.reward.contextMenuEvent = MethodType(self.onRewardContextMenuEvent, self.reward)

    def onRewardContextMenuEvent(self, list_widget, QContextMenuEvent):
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

    def onRewardItemChanged(self, item):
        row = self.reward.count() - 1
        character_entry = self.reward.item(row)
        # Only allow one entry, no characters allowed
        if self.db_list.isCharacter(character_entry.text()):
            self.reward.takeItem(row)
        elif self.reward.count() > 1:
            self.reward.takeItem(row - 1)

    def routeDirtiables(self, parent):
        self.onDirty = QAction(triggered=lambda: parent.setDirty([]))
        self.dialogue.textChanged.connect(parent.setDirty)
        self.reward.itemChanged.connect(parent.setDirty)
        self.gold_amount.valueChanged.connect(parent.setDirty)

    def serialize(self):
        self.dirty = False
        payload = OrderedDict([
            ("dialogue", self.dialogue.toPlainText()),
            ("reward", ["", -1]),
            ("gold", self.gold_amount.value())
        ])
        reward = self.reward.item(0)
        if reward != None:
            payload["reward"] = \
                [reward.text(), self.db_list.getEntryIconSource(reward.text())]
        return payload

    def unserialize(self, data):
        icon_generator = IconGenerator()
        self.dialogue.setText(data["dialogue"])
        if data["reward"][0] != "":
            icon = icon_generator.getIcon(data["reward"][1])
            self.reward.addItem(QListWidgetItem(icon, data["reward"][0]))
        self.gold_amount.setValue(int(data["gold"]))

