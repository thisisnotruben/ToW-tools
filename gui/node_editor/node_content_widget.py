# -*- coding: utf-8 -*-
"""A module containing base class for Node's content graphical representation. It also contains example of
overriden Text Widget which can pass to it's parent notification about currently being modified."""
from collections import OrderedDict
from node_editor.node_serializable import Serializable
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon


class QDMNodeContentWidget(QWidget, Serializable):
    """Base class for representation of the Node's graphics content. This class also provides layout
    for other widgets inside of a :py:class:`~node_editor.node_node.Node`"""
    def __init__(self, node:'Node', parent:QWidget=None):
        """
        :param node: reference to the :py:class:`~node_editor.node_node.Node`
        :type node: :py:class:`~node_editor.node_node.Node`
        :param parent: parent widget
        :type parent: QWidget

        :Instance Attributes:
            - **node** - reference to the :class:`~node_editor.node_node.Node`
            - **layout** - ``QLayout`` container
        """
        self.node = node
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        """Sets up layouts and widgets to be rendered in :py:class:`~node_editor.node_graphics_node.QDMGraphicsNode` class.
        """
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.wdg_quest_name_label = QLabel("Quest Name")
        self.wdg_quest_name = QLineEdit(self.wdg_quest_name_label)
        self.wdg_quest_name.setPlaceholderText(self.wdg_quest_name_label.text())

        self.wdg_quest_giver_label = QLabel("Quest Giver")
        self.wdg_quest_giver_combo_box = QComboBox(self.wdg_quest_giver_label)
        
        self.wdg_quest_content_label = QLabel("Quest Content")
        self.wdg_quest_content_tabs = QTabWidget(self.wdg_quest_content_label)
        self.wdg_quest_content_tabs.addTab(DialoguePanel(parent=self), "Dialogue")
        self.wdg_quest_content_tabs.addTab(ObjectivePanel(parent=self), "Objectives")
                
        self.layout.addWidget(self.wdg_quest_giver_label)
        self.layout.addWidget(self.wdg_quest_giver_combo_box)
        self.layout.addWidget(self.wdg_quest_name_label)
        self.layout.addWidget(self.wdg_quest_name)
        self.layout.addWidget(self.wdg_quest_content_label)
        self.layout.addWidget(self.wdg_quest_content_tabs)
        
    def serialize(self) -> OrderedDict:
        return OrderedDict([
        ])

    def deserialize(self, data:dict, hashmap:dict={}, restore_id:bool=True) -> bool:
        return True


class DialoguePanel(QGroupBox):
    def __init__(self, str="Quest Dialogue", parent=None):
        super().__init__(str, parent=parent)

        self.dialogue_options = {"Start":None, "Active":None,
            "Completed":None, "Delivered":None}
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        key_names = [*self.dialogue_options.keys()]
        
        self.dialogue_combo_box = QComboBox(self)
        self.dialogue_combo_box.addItems(key_names)
        self.dialogue_combo_box.currentIndexChanged.connect(self.onDialogueSwitch)
        self.layout.addWidget(self.dialogue_combo_box)

        for i in range(len(key_names)):
            self.dialogue_options[key_names[i]] = QTextEdit(self)
            self.dialogue_options[key_names[i]].setPlaceholderText("Quest %s" % key_names[i])
            self.layout.addWidget(self.dialogue_options[key_names[i]])
            self.dialogue_options[key_names[i]].hide()
        self.onDialogueSwitch(0)

    def onDialogueSwitch(self, index):
        current_text = self.dialogue_combo_box.currentText()
        for key in self.dialogue_options:
            if key == current_text:
                self.dialogue_options[key].show()
            else:
                self.dialogue_options[key].hide()


class ObjectivePanel(QGroupBox):
    def __init__(self, str="", parent=None):
        super().__init__(str, parent=parent)

        self.entries = []
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)

        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0,0,0,0)

        self.delete_button = QPushButton(self)
        self.delete_button.setIcon(QIcon.fromTheme("edit-delete"))
        
        self.up_button = QPushButton(self)
        self.up_button.setIcon(QIcon.fromTheme("go-up"))

        self.down_button = QPushButton(self)
        self.down_button.setIcon(QIcon.fromTheme("go-down"))

        self.objective_combo_box = QComboBox(self)

        self.layout.addWidget(self.objective_combo_box)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.up_button)
        self.button_layout.addWidget(self.down_button)
        self.layout.addLayout(self.button_layout)

        self.addEntry()
        self.entries[0].show()

    def addEntry(self):
        entry = ObjectiveEntry(parent=self)
        self.entries.append(entry)
        self.layout.addWidget(entry)
        entry.hide()

    def moveEntry(self, from_index, to_index):
        entry = self.entries.pop(from_index)
        self.entries.insert(to_index)


class ObjectiveEntry(QGroupBox):
    def __init__(self, str="Quest Objective", parent=None):
        super().__init__(str, parent=parent)

        self.minAmount = 1
        self.maxAmount = 100

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        
        self.objective_entry_type = QComboBox(self)

        self.objective_entry = QComboBox(self)

        self.objective_kind = QComboBox(self)

        self.objective_amount = QSpinBox(self)
        self.objective_amount.setMinimum(self.minAmount)
        self.objective_amount.setMaximum(self.maxAmount)

        self.layout.addWidget(self.objective_entry_type)
        self.layout.addWidget(self.objective_entry)
        self.layout.addWidget(self.objective_kind)
        self.layout.addWidget(self.objective_amount)

