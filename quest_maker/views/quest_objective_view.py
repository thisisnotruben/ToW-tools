# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './quest_maker/views/quest_objective_view.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_quest_objective(object):
    def setupUi(self, quest_objective):
        quest_objective.setObjectName("quest_objective")
        quest_objective.resize(200, 150)
        self.verticalLayout = QtWidgets.QVBoxLayout(quest_objective)
        self.verticalLayout.setObjectName("verticalLayout")
        self.world_object = QtWidgets.QListWidget(quest_objective)
        self.world_object.setMaximumSize(QtCore.QSize(16777215, 32))
        self.world_object.setFocusPolicy(QtCore.Qt.NoFocus)
        self.world_object.setAcceptDrops(True)
        self.world_object.setAlternatingRowColors(True)
        self.world_object.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.world_object.setObjectName("world_object")
        self.verticalLayout.addWidget(self.world_object)
        self.world_object_keep = QtWidgets.QCheckBox(quest_objective)
        self.world_object_keep.setObjectName("world_object_keep")
        self.verticalLayout.addWidget(self.world_object_keep)
        self.quest_type = QtWidgets.QComboBox(quest_objective)
        self.quest_type.setObjectName("quest_type")
        self.verticalLayout.addWidget(self.quest_type)
        self.amount = QtWidgets.QSpinBox(quest_objective)
        self.amount.setMinimum(1)
        self.amount.setMaximum(100)
        self.amount.setObjectName("amount")
        self.verticalLayout.addWidget(self.amount)
        self.extra_content_bttn = QtWidgets.QPushButton(quest_objective)
        self.extra_content_bttn.setObjectName("extra_content_bttn")
        self.verticalLayout.addWidget(self.extra_content_bttn)

        self.retranslateUi(quest_objective)
        QtCore.QMetaObject.connectSlotsByName(quest_objective)

    def retranslateUi(self, quest_objective):
        _translate = QtCore.QCoreApplication.translate
        quest_objective.setWindowTitle(_translate("quest_objective", "Quest Objective"))
        self.world_object_keep.setText(_translate("quest_objective", "Keep world object?"))
        self.extra_content_bttn.setText(_translate("quest_objective", "Extra Content"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    quest_objective = QtWidgets.QWidget()
    ui = Ui_quest_objective()
    ui.setupUi(quest_objective)
    quest_objective.show()
    sys.exit(app.exec_())
