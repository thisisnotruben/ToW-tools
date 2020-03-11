from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from calc_conf import *
from node_editor.utils import dumpException
from exporters.game_db import *
from exporters.path_manager import PathManager


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

        self.icon_atlas = QPixmap("/home/rubsz/tiled/Tides_of_War/non_map/assets/dev_icon/icons.png")
        self.icon_size = (16, 16)
        self.all_items = set()
        self.initUI()
        self.load_databases()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.search = QLineEdit(parent=self)
        self.search.textChanged.connect(self.onSearch)
        self.search.setPlaceholderText("Find")

        self.filter_db = QComboBox(self)
        self.filter_db.currentTextChanged.connect(self.onFilter)

        self.filter_type = QComboBox(self)
        self.filter_type.currentTextChanged.connect(self.onFilter)

        self.list_view = QListWidget(self)
        self.list_view.setAlternatingRowColors(True)
        self.list_view.setTabKeyNavigation(True)

        self.layout.addWidget(self.search)
        self.layout.addWidget(self.filter_db)
        self.layout.addWidget(self.filter_type)
        self.layout.addWidget(self.list_view)

    def load_databases(self):
        db_path = PathManager.get_paths()["db"]
        item_data = GameDB(db_path).get_database(DataBases.ITEMDB)
        spell_data = GameDB(db_path).get_database(DataBases.SPELLDB)

        types = set([item_data[item_name]["type"] for item_name in item_data.keys()])
        types = [item_type.capitalize() for item_type in types]
        types.append("All")

        merged_data = {**item_data, **spell_data}
        for item_name in merged_data:
            if item_name in item_data.keys():
                merged_data[item_name]["_DB"] = DataBases.ITEMDB.value
            else:
                merged_data[item_name]["_DB"] = DataBases.SPELLDB.value
            self.addItem(merged_data[item_name], int(merged_data[item_name]["icon"]), item_name)

        self.filter_db.addItems(sorted(["All", DataBases.ITEMDB.value, DataBases.SPELLDB.value]))
        self.filter_type.addItems(sorted(types))

    def onSearch(self, current_text):
        founded_items = set(self.list_view.findItems(current_text, Qt.MatchContains))

        db_filter = self.filter_db.currentText()
        if db_filter != "All":
            founded_items = set([entry for entry in founded_items if entry.data["_DB"] == db_filter])

        type_filter = self.filter_type.currentText()
        if self.filter_type.isVisible() and type_filter != "All":
            founded_items = set([entry for entry in founded_items if entry.data["type"].capitalize() == type_filter])
        
        for entry in founded_items:
            entry.setHidden(False)
        for entry in self.all_items - founded_items:
            entry.setHidden(True)

    def onFilter(self, text):
        if text == DataBases.SPELLDB.value or text == "All":
            self.filter_type.hide()
        elif text == DataBases.ITEMDB.value:
            self.filter_type.show()
        self.onSearch(self.search.text())

    def addItem(self, data, icon_idx, label):
        width = self.icon_atlas.width() / self.icon_size[0]
        rect = QRect(icon_idx % width * self.icon_size[0], icon_idx // width * self.icon_size[1], *self.icon_size)
        icon = QIcon(self.icon_atlas.copy(rect))
        entry = DataEntry(data, self.list_view.count(), icon, label, self.list_view)
        self.list_view.addItem(entry)
        self.all_items.add(entry)
