# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './quest_maker/views/quest_character_content_view.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_quest_character_content(object):
    def setupUi(self, quest_character_content):
        quest_character_content.setObjectName("quest_character_content")
        quest_character_content.resize(300, 250)
        quest_character_content.setMinimumSize(QtCore.QSize(300, 250))
        quest_character_content.setMaximumSize(QtCore.QSize(16777215, 350))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("./quest_maker/views/../../icon.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        quest_character_content.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(quest_character_content)
        self.verticalLayout.setObjectName("verticalLayout")
        self.dialogue = QtWidgets.QTextEdit(quest_character_content)
        self.dialogue.setObjectName("dialogue")
        self.verticalLayout.addWidget(self.dialogue)
        self.reward_lbl = QtWidgets.QLabel(quest_character_content)
        self.reward_lbl.setObjectName("reward_lbl")
        self.verticalLayout.addWidget(self.reward_lbl)
        self.reward = QtWidgets.QListWidget(quest_character_content)
        self.reward.setMaximumSize(QtCore.QSize(16777215, 32))
        self.reward.setAcceptDrops(True)
        self.reward.setAlternatingRowColors(True)
        self.reward.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.reward.setObjectName("reward")
        self.verticalLayout.addWidget(self.reward)
        self.gold_amount_lbl = QtWidgets.QLabel(quest_character_content)
        self.gold_amount_lbl.setObjectName("gold_amount_lbl")
        self.verticalLayout.addWidget(self.gold_amount_lbl)
        self.gold_amount = QtWidgets.QSpinBox(quest_character_content)
        self.gold_amount.setMaximum(1000)
        self.gold_amount.setObjectName("gold_amount")
        self.verticalLayout.addWidget(self.gold_amount)

        self.retranslateUi(quest_character_content)
        QtCore.QMetaObject.connectSlotsByName(quest_character_content)

    def retranslateUi(self, quest_character_content):
        _translate = QtCore.QCoreApplication.translate
        quest_character_content.setWindowTitle(_translate("quest_character_content", "Content"))
        self.dialogue.setPlaceholderText(_translate("quest_character_content", "Dialogue"))
        self.reward_lbl.setText(_translate("quest_character_content", "Reward"))
        self.reward.setToolTip(_translate("quest_character_content", "Cannot be a character"))
        self.gold_amount_lbl.setText(_translate("quest_character_content", "Gold Amount"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    quest_character_content = QtWidgets.QWidget()
    ui = Ui_quest_character_content()
    ui.setupUi(quest_character_content)
    quest_character_content.show()
    sys.exit(app.exec_())
