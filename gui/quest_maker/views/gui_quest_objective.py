# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui_quest_objective.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(185, 155)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.world_object = QtWidgets.QListWidget(Form)
        self.world_object.setAcceptDrops(True)
        self.world_object.setAlternatingRowColors(True)
        self.world_object.setObjectName("world_object")
        self.verticalLayout.addWidget(self.world_object)
        self.quest_type = QtWidgets.QComboBox(Form)
        self.quest_type.setObjectName("quest_type")
        self.verticalLayout.addWidget(self.quest_type)
        self.amount = QtWidgets.QSpinBox(Form)
        self.amount.setMinimum(1)
        self.amount.setMaximum(100)
        self.amount.setObjectName("amount")
        self.verticalLayout.addWidget(self.amount)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
