# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './content_maker/views/quest_node_objective_content_view.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_objective_content_view(object):
    def setupUi(self, objective_content_view):
        objective_content_view.setObjectName("objective_content_view")
        objective_content_view.resize(300, 250)
        objective_content_view.setMinimumSize(QtCore.QSize(300, 250))
        objective_content_view.setMaximumSize(QtCore.QSize(16777215, 350))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./content_maker/views/../../icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        objective_content_view.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(objective_content_view)
        self.verticalLayout.setObjectName("verticalLayout")
        self.dialogue = QtWidgets.QTextEdit(objective_content_view)
        self.dialogue.setEnabled(False)
        self.dialogue.setObjectName("dialogue")
        self.verticalLayout.addWidget(self.dialogue)
        self.reward_lbl = QtWidgets.QLabel(objective_content_view)
        self.reward_lbl.setObjectName("reward_lbl")
        self.verticalLayout.addWidget(self.reward_lbl)
        self.reward = QtWidgets.QListWidget(objective_content_view)
        self.reward.setMaximumSize(QtCore.QSize(16777215, 32))
        self.reward.setAcceptDrops(True)
        self.reward.setAlternatingRowColors(True)
        self.reward.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.reward.setObjectName("reward")
        self.verticalLayout.addWidget(self.reward)
        self.gold_amount_lbl = QtWidgets.QLabel(objective_content_view)
        self.gold_amount_lbl.setObjectName("gold_amount_lbl")
        self.verticalLayout.addWidget(self.gold_amount_lbl)
        self.gold_amount = QtWidgets.QSpinBox(objective_content_view)
        self.gold_amount.setMaximum(10000)
        self.gold_amount.setObjectName("gold_amount")
        self.verticalLayout.addWidget(self.gold_amount)

        self.retranslateUi(objective_content_view)
        QtCore.QMetaObject.connectSlotsByName(objective_content_view)

    def retranslateUi(self, objective_content_view):
        _translate = QtCore.QCoreApplication.translate
        objective_content_view.setWindowTitle(_translate("objective_content_view", "Content"))
        self.dialogue.setPlaceholderText(_translate("objective_content_view", "Dialogue"))
        self.reward_lbl.setText(_translate("objective_content_view", "Reward"))
        self.reward.setToolTip(_translate("objective_content_view", "Cannot be a character"))
        self.gold_amount_lbl.setText(_translate("objective_content_view", "Gold Amount"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    objective_content_view = QtWidgets.QWidget()
    ui = Ui_objective_content_view()
    ui.setupUi(objective_content_view)
    objective_content_view.show()
    sys.exit(app.exec_())
