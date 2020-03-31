#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from collections import OrderedDict
from PyQt5.QtWidgets import QWidget, QMessageBox, QAction, QListWidgetItem
from PyQt5.QtCore import Qt

from content_maker.views.character_content_node_view import Ui_character_content_node
from content_maker.metas import ISerializable, Dirty
from content_maker.icon_generator import IconGenerator


class CharacterContentNode(QWidget, Ui_character_content_node, ISerializable, Dirty):
    
    def __init__(self, db_list, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)
        Dirty.__init__(self)
        self.db_list = db_list
        self.setupUi(self)

    def setupUi(self, character_content_node):
        super().setupUi(character_content_node)
        # route drops signals
        self.character_list.itemChanged.connect(self.onCharacterDrop)
        self.drops_list.itemChanged.connect(self.onWorldObjectDrop)
        self.merchandise_list.itemChanged.connect(self.onWorldObjectDrop)
        self.spells_list.itemChanged.connect(self.onSpellsDrop)
        # setup delete button function
        self.on_delete_confirm = QAction()
        self.delete_node_bttn.clicked.connect(self.deleteNode)

    def deleteNode(self, bypass_prompt=False):
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
        
    def deleteCharacter(self, list_widget, listWidgetItem):
        # delete character entry
        if self.db_list.isCharacter(listWidgetItem.text()):
            list_widget.takeItem(list_widget.count() - 1)

    def onCharacterDrop(self, listWidgetItem):
        # only one character allowed here
        row = self.character_list.count() - 1
        if not self.db_list.isCharacter(listWidgetItem.text()):
            self.character_list.takeItem(row)
        elif self.character_list.count()> 1:
            self.character_list.takeItem(row - 1)

    def onWorldObjectDrop(self, listWidgetItem):
        # allow anything other then characters
        def deleteCharacter(list_widget, listWidgetItem):
            if self.db_list.isCharacter(listWidgetItem.text()):
                list_widget.takeItem(list_widget.count() - 1)
        deleteCharacter(self.drops_list, listWidgetItem)
        deleteCharacter(self.merchandise_list, listWidgetItem)

    def onSpellsDrop(self, listWidgetItem):
        # allow only spells here
        if not self.db_list.isSpell(listWidgetItem.text()):
            self.spells_list.takeItem(self.spells_list.count() - 1)

    def routeDirtiables(self, parent):
        self.onDirty = QAction(triggered=lambda: parent.setDirty([]))
        self.move_node_left_bttn.clicked.connect(parent.setDirty)
        self.move_node_right_bttn.clicked.connect(parent.setDirty)

        self.character_list.itemChanged.connect(parent.setDirty)
        self.level.valueChanged.connect(parent.setDirty)
        self.enemy.stateChanged.connect(parent.setDirty)
        self.healer.stateChanged.connect(parent.setDirty)
        self.healer_gold_amount.valueChanged.connect(parent.setDirty)
        self.dialogue.textChanged.connect(parent.setDirty)
        self.drops_list.itemChanged.connect(parent.setDirty)
        self.spells_list.itemChanged.connect(parent.setDirty)
        self.merchandise_list.itemChanged.connect(parent.setDirty)

    def serialize(self):

        def getItemData(list_widget):
            itemData = []
            for i in range(list_widget.count()):
                entry_text = list_widget.item(i).text()
                itemData.append([entry_text, \
                    self.db_list.getEntryIconSource(entry_text)])
            if len(itemData) == 0:
                itemData.append(["", -1])
            return itemData

        payload = OrderedDict([
            ("character", getItemData(self.character_list)[0]),
            ("level", self.level.value()),
            ("enemy", self.enemy.isChecked()),
            ("healer", self.healer.isChecked()),
            ("healer_gold_amount", self.healer_gold_amount.value()),
            ("dialogue", self.dialogue.toPlainText()),
            ("drops", getItemData(self.drops_list)),
            ("spells", getItemData(self.spells_list)),
            ("merchandise", getItemData(self.merchandise_list))
        ])
        return payload

    def unserialize(self, data):

        icon_generator = IconGenerator()
        def unpackItemData(list_widget, serialized_list_data):
            icon = icon_generator.getIcon(serialized_list_data[1])
            list_widget.addItem(QListWidgetItem(icon, serialized_list_data[0]))

        if data["character"][0] != "":
            unpackItemData(self.character_list, data["character"])

        self.level.setValue(int(data["level"]))
        self.enemy.setChecked(bool(data["enemy"]))
        self.healer.setChecked(bool(data["healer"]))
        self.healer_gold_amount.setValue(int(data["healer_gold_amount"]))
        self.dialogue.setText(data["dialogue"])

        if data["drops"][0] != "":
            unpackItemData(self.drops_list, data["drops"])

        if data["spells"][0] != "":
            unpackItemData(self.spells_list, data["spells"])

        if data["merchandise"][0] != "":
            unpackItemData(self.merchandise_list, data["merchandise"])

