#!/usr/bin/env python3

from os.path import isfile
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QIcon, QPixmap

from core.path_manager import PathManager


class IconGenerator:

	icon_size = (16, 16)

	def __init__(self):
		super().__init__()
		self.icon_atlas = QPixmap(PathManager.get_paths()["icon_atlas_data"]["path"])
		self.atlas_cell_width = self.icon_atlas.width() / IconGenerator.icon_size[0]

	def getIcon(self, icon_data):
		icon = QIcon()
		if type(icon_data) == int and icon_data != -1:
			rect = QRect(
				int(icon_data % self.atlas_cell_width * IconGenerator.icon_size[0]),
				int(icon_data // self.atlas_cell_width * IconGenerator.icon_size[1]),
				*IconGenerator.icon_size)
			icon = QIcon(self.icon_atlas.copy(rect))
		elif isfile(icon_data):
			icon = QIcon(icon_data)
		return icon

