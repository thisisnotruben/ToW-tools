# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './quest_maker/views/quest_main_view.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_quest_maker_main(object):
    def setupUi(self, quest_maker_main):
        quest_maker_main.setObjectName("quest_maker_main")
        quest_maker_main.resize(1200, 800)
        self.central_widget = QtWidgets.QWidget(quest_maker_main)
        self.central_widget.setObjectName("central_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.central_widget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.horizontalLayout.setContentsMargins(9, -1, -1, 9)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.db_layout = QtWidgets.QVBoxLayout()
        self.db_layout.setSpacing(4)
        self.db_layout.setObjectName("db_layout")
        self.search = QtWidgets.QLineEdit(self.central_widget)
        self.search.setObjectName("search")
        self.db_layout.addWidget(self.search)
        self.filter_db = QtWidgets.QComboBox(self.central_widget)
        self.filter_db.setCurrentText("")
        self.filter_db.setObjectName("filter_db")
        self.db_layout.addWidget(self.filter_db)
        self.filter_type = QtWidgets.QComboBox(self.central_widget)
        self.filter_type.setObjectName("filter_type")
        self.db_layout.addWidget(self.filter_type)
        self.filter_sub_type = QtWidgets.QComboBox(self.central_widget)
        self.filter_sub_type.setObjectName("filter_sub_type")
        self.db_layout.addWidget(self.filter_sub_type)
        self.list_view = QtWidgets.QListWidget(self.central_widget)
        self.list_view.setDragEnabled(True)
        self.list_view.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setProperty("isWrapping", False)
        self.list_view.setModelColumn(0)
        self.list_view.setObjectName("list_view")
        self.db_layout.addWidget(self.list_view)
        self.horizontalLayout.addLayout(self.db_layout)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.controls = QtWidgets.QHBoxLayout()
        self.controls.setObjectName("controls")
        self.add_quest_node_bttn = QtWidgets.QPushButton(self.central_widget)
        self.add_quest_node_bttn.setObjectName("add_quest_node_bttn")
        self.controls.addWidget(self.add_quest_node_bttn)
        self.undo_save_bttn = QtWidgets.QPushButton(self.central_widget)
        self.undo_save_bttn.setObjectName("undo_save_bttn")
        self.controls.addWidget(self.undo_save_bttn)
        self.redo_save_bttn = QtWidgets.QPushButton(self.central_widget)
        self.redo_save_bttn.setObjectName("redo_save_bttn")
        self.controls.addWidget(self.redo_save_bttn)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.controls.addItem(spacerItem)
        self.verticalLayout.addLayout(self.controls)
        self.scrollArea = QtWidgets.QScrollArea(self.central_widget)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scroll_area_widget = QtWidgets.QWidget()
        self.scroll_area_widget.setGeometry(QtCore.QRect(0, 0, 976, 698))
        self.scroll_area_widget.setObjectName("scroll_area_widget")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.scroll_area_widget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.scroll_layout = QtWidgets.QHBoxLayout()
        self.scroll_layout.setObjectName("scroll_layout")
        self.horizontalLayout_3.addLayout(self.scroll_layout)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.scrollArea.setWidget(self.scroll_area_widget)
        self.verticalLayout.addWidget(self.scrollArea)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 5)
        quest_maker_main.setCentralWidget(self.central_widget)
        self.menu_bar = QtWidgets.QMenuBar(quest_maker_main)
        self.menu_bar.setGeometry(QtCore.QRect(0, 0, 1200, 22))
        self.menu_bar.setObjectName("menu_bar")
        self.menu_file = QtWidgets.QMenu(self.menu_bar)
        self.menu_file.setObjectName("menu_file")
        self.menu_help = QtWidgets.QMenu(self.menu_bar)
        self.menu_help.setObjectName("menu_help")
        self.menuEdit = QtWidgets.QMenu(self.menu_bar)
        self.menuEdit.setObjectName("menuEdit")
        quest_maker_main.setMenuBar(self.menu_bar)
        self.status_bar = QtWidgets.QStatusBar(quest_maker_main)
        self.status_bar.setObjectName("status_bar")
        quest_maker_main.setStatusBar(self.status_bar)
        self.action_new = QtWidgets.QAction(quest_maker_main)
        self.action_new.setObjectName("action_new")
        self.action_open = QtWidgets.QAction(quest_maker_main)
        self.action_open.setObjectName("action_open")
        self.action_save = QtWidgets.QAction(quest_maker_main)
        self.action_save.setObjectName("action_save")
        self.action_save_As = QtWidgets.QAction(quest_maker_main)
        self.action_save_As.setObjectName("action_save_As")
        self.action_about = QtWidgets.QAction(quest_maker_main)
        self.action_about.setObjectName("action_about")
        self.action_quit = QtWidgets.QAction(quest_maker_main)
        self.action_quit.setObjectName("action_quit")
        self.action_undo = QtWidgets.QAction(quest_maker_main)
        self.action_undo.setObjectName("action_undo")
        self.action_redo = QtWidgets.QAction(quest_maker_main)
        self.action_redo.setObjectName("action_redo")
        self.menu_file.addAction(self.action_new)
        self.menu_file.addAction(self.action_open)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_save)
        self.menu_file.addAction(self.action_save_As)
        self.menu_file.addSeparator()
        self.menu_file.addAction(self.action_quit)
        self.menu_help.addAction(self.action_about)
        self.menuEdit.addAction(self.action_undo)
        self.menuEdit.addAction(self.action_redo)
        self.menu_bar.addAction(self.menu_file.menuAction())
        self.menu_bar.addAction(self.menuEdit.menuAction())
        self.menu_bar.addAction(self.menu_help.menuAction())

        self.retranslateUi(quest_maker_main)
        self.filter_db.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(quest_maker_main)

    def retranslateUi(self, quest_maker_main):
        _translate = QtCore.QCoreApplication.translate
        quest_maker_main.setWindowTitle(_translate("quest_maker_main", "Tides of War Quest Maker"))
        self.search.setPlaceholderText(_translate("quest_maker_main", "Find"))
        self.add_quest_node_bttn.setText(_translate("quest_maker_main", "Add Quest Node"))
        self.undo_save_bttn.setText(_translate("quest_maker_main", "Undo Save"))
        self.redo_save_bttn.setText(_translate("quest_maker_main", "Redo Save"))
        self.menu_file.setTitle(_translate("quest_maker_main", "File"))
        self.menu_help.setTitle(_translate("quest_maker_main", "Help"))
        self.menuEdit.setTitle(_translate("quest_maker_main", "Edit"))
        self.action_new.setText(_translate("quest_maker_main", "New"))
        self.action_new.setShortcut(_translate("quest_maker_main", "Ctrl+N"))
        self.action_open.setText(_translate("quest_maker_main", "Open"))
        self.action_open.setShortcut(_translate("quest_maker_main", "Ctrl+O"))
        self.action_save.setText(_translate("quest_maker_main", "Save"))
        self.action_save.setShortcut(_translate("quest_maker_main", "Ctrl+S"))
        self.action_save_As.setText(_translate("quest_maker_main", "Save As"))
        self.action_save_As.setShortcut(_translate("quest_maker_main", "Ctrl+Shift+S"))
        self.action_about.setText(_translate("quest_maker_main", "About"))
        self.action_quit.setText(_translate("quest_maker_main", "Quit"))
        self.action_quit.setShortcut(_translate("quest_maker_main", "Ctrl+Q"))
        self.action_undo.setText(_translate("quest_maker_main", "Undo Save"))
        self.action_undo.setShortcut(_translate("quest_maker_main", "Ctrl+Z"))
        self.action_redo.setText(_translate("quest_maker_main", "Redo Save"))
        self.action_redo.setShortcut(_translate("quest_maker_main", "Ctrl+Shift+Z"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    quest_maker_main = QtWidgets.QMainWindow()
    ui = Ui_quest_maker_main()
    ui.setupUi(quest_maker_main)
    quest_maker_main.show()
    sys.exit(app.exec_())
