import os
import sys
from PyQt5.QtWidgets import *

gui_dir = os.path.join(os.path.dirname(__file__), os.pardir)
sys.path.insert(0, gui_dir)
sys.path.append(os.path.join(gui_dir, os.pardir))

from calc_window import CalculatorWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # print(QStyleFactory.keys())
    app.setStyle('Fusion')

    wnd = CalculatorWindow()
    wnd.show()

    sys.exit(app.exec_())
