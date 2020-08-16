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

from exporter.views.exporter_main_view import Ui_MainWindow

from core.path_manager import PathManager
from core.main import Main


class Thread(QThread):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.main = Main()
        self.print_redirect = StringIO()
        self.command = ""
        self.args = []
        self.output = ""

    def run(self):
        sys.stdout = self.print_redirect
        self.main.execute_command(self.command, *self.args)
        sys.stdout = sys.__stdout__
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

        self.action_quit.triggered.connect(MainWindow.close)

        # set style sheet
        root_dir = os.path.join(os.path.dirname(__file__), os.pardir)
        path = os.path.join(root_dir, "QTDark-master", "QTDark.stylesheet")
        with open(path, "r") as f:
            MainWindow.setStyleSheet(f.read())

    def setup_tool(self):
        self.buttons = [self.make_sprite_icons, self.make_sprite_deaths, self.make_sym_links, 
            self.make_icon_atlas, self.archive, self.export_map, self.export_db, self.debug_map,
            self.make_tilesets, self.export_content, self.make_lid]

        self.make_sprite_icons.clicked.connect(lambda: self.onOpenFileDialog(self.make_sprite_icons.toolTip(), True))
        self.make_sprite_deaths.clicked.connect(lambda : self.onOpenFileDialog(self.make_sprite_deaths.toolTip(), True))
        self.make_lid.clicked.connect(lambda : self.onOpenFileDialog(self.make_lid.toolTip()))
        self.make_sym_links.clicked.connect(lambda : self.onClick(self.make_sym_links.toolTip()))
        self.make_icon_atlas.clicked.connect(lambda : self.onClick(self.make_icon_atlas.toolTip()))
        self.archive.clicked.connect(lambda : self.onClick(self.archive.toolTip()))
        self.export_map.clicked.connect(lambda : self.onOpenFileDialog(self.export_map.toolTip(), False))
        self.export_tilesets.clicked.connect(lambda : self.onClick(self.export_tilesets.toolTip()))
        self.export_db.clicked.connect(lambda : self.onClick(self.export_db.toolTip()))
        self.debug_map.clicked.connect(lambda : self.onClick(self.debug_map.toolTip()))
        self.make_tilesets.clicked.connect(lambda : self.onClick(self.make_tilesets.toolTip()))
        self.export_content.clicked.connect(lambda : self.onClick(self.export_content.toolTip()))

        self.thread = Thread(self.main_window)
        self.thread.finished.connect(self.onCommandFinished)

    def onOpenFileDialog(self, command: str, spriteSheet: bool):

        dialogue = {
            "header":  "Open a SpriteSheet",
            "openPath": PathManager.get_paths()["game"]["character_dir"],
            "fileType": "png (*.png)"
        }
        if not spriteSheet:
            dialogue = {
                "header": "Maps to export",
                "openPath": PathManager.get_paths()["tiled"]["map_dir"],
                "fileType": "tmx (*.tmx)"
            }

        files = QFileDialog.getOpenFileNames(self.main_window, dialogue["header"], dialogue["openPath"], dialogue["fileType"])
        file_paths = files[0]
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
    # make app
    app = QApplication(sys.argv)
    ui = MainWindow()

    # exec app
    sys.exit(app.exec_())
    