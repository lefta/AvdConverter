#!/bin/env python3

import sys
from PyQt5.QtWidgets import QApplication
from lib.Window import Window

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    sys.exit(app.exec_())
