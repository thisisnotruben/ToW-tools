#!/usr/bin/env python3
"""
Ruben Alvarez Reyes
"""

from os.path import isfile
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QIcon, QPixmap

from core.path_manager import PathManager


class IconGenerator:

    icon_size = (16, 16)

    def __init__(self):
        super().__init__()
        self.icon_atlas = QPixmap(
            PathManager.get_paths()["icon_atlas_data"]["path"]
        )
        self.atlas_cell_width = \
            self.icon_atlas.width() / IconGenerator.icon_size[0]

    def getIcon(self, icon_data):
        icon = QIcon()
        if type(icon_data) == int and icon_data != -1:
            rect = QRect(icon_data % self.atlas_cell_width * IconGenerator.icon_size[0], # x
                icon_data // self.atlas_cell_width * IconGenerator.icon_size[1],         # y
                *IconGenerator.icon_size)                                                # w, h
            icon = QIcon(self.icon_atlas.copy(rect))
        elif isfile(icon_data):
            icon = QIcon(icon_data)
        return icon

