#!/usr/bin/env python3

import os
import sys
import enum
from io import StringIO
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtGui import QTextCursor, QIcon
from PyQt5.QtCore import QThread, QDir

from exporter.views.exporter_main_view import Ui_MainWindow

from core.path_manager import PathManager
from main import Main


class FileDialogueType(enum.Enum):
	SPRITE_SHEET = enum.auto()
	MAP = enum.auto()
	CONTENT = enum.auto()
	QUEST = enum.auto()


class Thread(QThread):
	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.main = Main()
		self.print_redirect = StringIO()
		self.command = ""
		self.args = []
		self.output = ""
		self.main.db.conn.close()
		self.main.db._load_db(False)

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

		about_popup = lambda: QMessageBox.about(self.main_window, "About", self.about)
		self.action_about.triggered.connect(about_popup)

		self.action_quit.triggered.connect(MainWindow.close)

		# set style sheet / icon
		rootDir: str = os.path.dirname(__file__)

		self.main_window.setWindowIcon(QIcon(os.path.join(rootDir, "icon.png")))
		with open(os.path.join(rootDir, "QTDark-master", "QTDark.stylesheet"), "r") as f:
			MainWindow.setStyleSheet(f.read())

	def setup_tool(self):
		self.buttons = [self.make_sprite_icons, self.make_sprite_deaths, self.make_sym_links,
			self.make_icon_atlas, self.archive, self.export_map, self.export_db, self.debug_map,
			self.make_tilesets, self.export_content, self.make_lid]

		self.make_sprite_icons.clicked.connect(lambda: self.onOpenFileDialog(self.make_sprite_icons.toolTip(), FileDialogueType.SPRITE_SHEET))
		self.make_sprite_deaths.clicked.connect(lambda : self.onOpenFileDialog(self.make_sprite_deaths.toolTip(), FileDialogueType.SPRITE_SHEET))
		self.make_lid.clicked.connect(lambda : self.onOpenFileDialog(self.make_lid.toolTip(), FileDialogueType.SPRITE_SHEET))
		self.make_sym_links.clicked.connect(lambda : self.onClick(self.make_sym_links.toolTip()))
		self.make_icon_atlas.clicked.connect(lambda : self.onClick(self.make_icon_atlas.toolTip()))
		self.archive.clicked.connect(lambda : self.onClick(self.archive.toolTip()))
		self.export_map.clicked.connect(lambda : self.onOpenFileDialog(self.export_map.toolTip(), FileDialogueType.MAP))
		self.export_tilesets.clicked.connect(lambda : self.onClick(self.export_tilesets.toolTip()))
		self.export_db.clicked.connect(lambda : self.onClick(self.export_db.toolTip()))
		self.debug_map.clicked.connect(lambda : self.onClick(self.debug_map.toolTip()))
		self.make_tilesets.clicked.connect(lambda : self.onClick(self.make_tilesets.toolTip()))
		self.export_content.clicked.connect(lambda : self.onOpenFileDialog(self.export_content.toolTip(), FileDialogueType.CONTENT))
		self.export_quest.clicked.connect(lambda : self.onOpenFileDialog(self.export_quest.toolTip(), FileDialogueType.QUEST))
		self.export_raw_audio.clicked.connect(lambda : self.onClick(self.export_raw_audio.toolTip()))

		self.thread = Thread(self.main_window)
		self.thread.finished.connect(self.onCommandFinished)

	def onOpenFileDialog(self, command: str, dialogueType: FileDialogueType):

		dialogue = {
			"header":"NOT SET",
			"openPath": QDir().homePath(),
			"fileType": "ALL (*.*)"
		}

		pM: dict = PathManager.get_paths()

		if dialogueType == FileDialogueType.SPRITE_SHEET:
			dialogue["header"] = "Open SpriteSheets"
			dialogue["openPath"] = pM["game"]["character_dir"]
			dialogue["fileType"] = "png (*.png)"
		elif dialogueType == FileDialogueType.MAP:
			dialogue["header"] = "Maps to export"
			dialogue["openPath"] = pM["tiled"]["map_dir"]
			dialogue["fileType"] = "tmx (*.tmx)"
		elif dialogueType == FileDialogueType.CONTENT:
			dialogue["header"] = "Contents to export"
			dialogue["openPath"] = pM["character_content_dir"]
			dialogue["fileType"] = "json (*.json)"
		elif dialogueType == FileDialogueType.QUEST:
			dialogue["header"] = "Quests to export"
			dialogue["openPath"] = pM["quest_content_dir"]
			dialogue["fileType"] = "json (*.json)"

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
