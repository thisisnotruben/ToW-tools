from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from quest_maker.calc_conf import *
from node_editor.utils import dumpException


class DataEntry(QListWidgetItem):
    def __init__(self, data, index, QIcon, str, parent=None, type=QListWidgetItem.Type):
        super().__init__(QIcon, str, parent=parent, type=type)
        self.data = data
        self.index = index

    def __hash__(self):
        return self.index


class DataView(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent=parent, flags=flags)

        self.icon_atlas = QPixmap(
            "/home/rubsz/tiled/Tides_of_War/non_map/assets/dev_icon/icons.png")
        self.icon_size = (16, 16)
        self.all_items = set()
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.search = QLineEdit(parent=self)
        self.search.textChanged.connect(self.onSearch)
        self.search.setPlaceholderText("Find")
        self.filter_db = QComboBox(self)
        self.filter_type = QComboBox(self)
        self.filter_sub_type = QComboBox(self)
        self.list_view = QListWidget(self)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setTabKeyNavigation(True)
        self.list_view.setIconSize(QSize(64, 64))

        for i in range(1790 + 1):
            self.addItem({}, i, "Data Entry %d" % i)

        self.layout.addWidget(self.search)
        self.layout.addWidget(self.filter_db)
        self.layout.addWidget(self.filter_type)
        self.layout.addWidget(self.filter_sub_type)
        self.layout.addWidget(self.list_view)

    def onSearch(self, current_text):
        founded_items = set(self.list_view.findItems(current_text, Qt.MatchContains))
        for entry in founded_items:
            entry.setHidden(False)
        for entry in self.all_items - founded_items:
            entry.setHidden(True)

    def addItem(self, data, icon_idx, label):
        width = self.icon_atlas.width() / self.icon_size[0]
        rect = QRect(icon_idx % width * self.icon_size[0], icon_idx // width * self.icon_size[1], *self.icon_size)
        icon = QIcon(self.icon_atlas.copy(rect))
        entry = DataEntry(data, self.list_view.count(), icon, label, self.list_view)
        self.list_view.addItem(entry)
        self.all_items.add(entry)
