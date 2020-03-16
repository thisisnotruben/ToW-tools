#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from types import MethodType
from PyQt5.QtWidgets import QWidget, QListWidgetItem, QMenu

from gui.quest_maker.views.gui_quest_node import Ui_quest_node
from gui.quest_maker.views.gui_quest_objective import Ui_Form


class QuestObjective(Ui_Form, QWidget):
    def __init__(self):
        super().__init__()  
        self.setupUi(self)
        self.show()

    def setupUi(self, Form):
        super().setupUi(Form)


class QuestNode(Ui_quest_node, QWidget):

    def __init__(self, db_list):
        super().__init__()
        self.dropEventMap = {}
        self.all_objectives = []
        self.db_list = db_list
        self.setupUi(self)
        self.show()
                
    def setupUi(self, quest_node):
        super().setupUi(quest_node)
        self.objective_list.contextMenuEvent = MethodType(self.objectiveContextMenu, self.objective_list)
        self.add_objective_bttn.clicked.connect(self.onAddObjective)
        self.mapDropEvent(self.giver_list)
        self.mapDropEvent(self.receiver_list)
        self.onAddObjective()

    def objectiveContextMenu(self, objective_list, event):
        menu = QMenu(self)
        add_action = menu.addAction("Add")
        delete_action = menu.addAction("Delete")
        menu.addSeparator()
        move_up_action = menu.addAction("Move Up")
        move_down_action = menu.addAction("Move Down")

        action = menu.exec_(self.mapToGlobal(event.pos()))

    def onAddObjective(self):
        objective = QuestObjective()
        entry = QListWidgetItem(self.objective_list)
        entry.setSizeHint(objective.minimumSizeHint())
        self.objective_list.addItem(entry)
        self.objective_list.setItemWidget(entry, objective)
        self.all_objectives.append(objective)
        self.mapDropEvent(objective.world_object)

    def mapDropEvent(self, list_widget):
        self.dropEventMap[list_widget] = list_widget.dropEvent
        list_widget.dropEvent = MethodType(self.onDropEvent, list_widget)

    def onDropEvent(self, list_widget, event):
        self.dropEventMap[list_widget](event)
        row = list_widget.count() - 1
        entry = list_widget.item(row) 
        charOnlyEntry = list_widget in [self.giver_list, self.receiver_list]
        if not self.db_list.isCharacter(entry.text()) and charOnlyEntry:
            list_widget.takeItem(row)
        elif list_widget.count() > 1:
            list_widget.takeItem(row - 1)

