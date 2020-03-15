#!/usr/bin/env python3
"""
Ruben Alvaerz Reyes
"""

import os
import sys
from io import StringIO
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QSystemTrayIcon
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtCore import QThread

sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))

from gui.tool_gui import Ui_MainWindow
from exporters.main import Main


class Thread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.main = Main()
        self.print_redirect = StringIO()
        self.reg_stdout = sys.stdout
        self.command = ""
        self.args = []
        self.output = ""

    def run(self):
        sys.stdout = self.print_redirect
        self.main.execute_command(self.command, *self.args)
        sys.stdout = self.reg_stdout
        self.output = self.print_redirect.getvalue()

class MainWindow(Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.main_window = QMainWindow()
        self.setupUi(self.main_window)
        self.setup_tool()
        self.main_window.show()
        self.about = "Author: Ruben Alvarez Reyes<br/>Source: " \
            "<a href=\"https://github.com/thisisnotruben/ToW-tools/\">Github</a>"

    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)

        icon = QIcon(os.path.join(os.path.dirname(__file__), os.pardir, "icon.png"))
        self.main_window.setWindowIcon(icon)

        about_popup = lambda: QMessageBox.about(self.main_window, "About", self.about)
        self.action_about.triggered.connect(about_popup)

    def setup_tool(self):
        self.buttons = [self.make_sprite_icons, self.make_sprite_deaths, self.make_sym_links, 
            self.make_icon_atlas, self.archive, self.export_map, self.export_db, self.debug_map]

        self.make_sprite_icons.clicked.connect(lambda: self.onClick(self.make_sprite_icons.toolTip()))
        self.make_sprite_deaths.clicked.connect(lambda : self.onMakeSpriteDeaths(self.make_sprite_deaths.toolTip()))
        self.make_sym_links.clicked.connect(lambda : self.onClick(self.make_sym_links.toolTip()))
        self.make_icon_atlas.clicked.connect(lambda : self.onClick(self.make_icon_atlas.toolTip()))
        self.archive.clicked.connect(lambda : self.onClick(self.archive.toolTip()))
        self.export_map.clicked.connect(lambda : self.onClick(self.export_map.toolTip()))
        self.export_db.clicked.connect(lambda : self.onClick(self.export_db.toolTip()))
        self.debug_map.clicked.connect(lambda : self.onClick(self.debug_map.toolTip()))

        self.thread = Thread(self.main_window)
        self.thread.finished.connect(self.onCommandFinished)

    def onMakeSpriteDeaths(self, command):
        self.files = QFileDialog.getOpenFileNames(self.main_window, "Open a SpriteSheet", \
            "/home/rubsz/godot/my_games/Tides_of_War/asset/img/character", "png (*.png)")
        file_paths = self.files[0]
        if len(file_paths) > 0:
            self.onClick(command, file_paths)

    def onCommandFinished(self):
        self.terminal_output.setText(self.thread.output)
        self.terminal_output.moveCursor(QTextCursor.End)
        self.enableButtons(True)

    def onClick(self, command, args=[]):
        self.enableButtons(False)
        self.thread.command = command
        self.thread.args = args
        self.thread.start()

    def enableButtons(self, enable):
        for button in self.buttons:
            button.setEnabled(enable)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainWindow()
    sys.exit(app.exec_())
    