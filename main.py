# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sys

from PyQt5.QtWidgets import QApplication

from gui import SynchroniseWindow

if __name__ == '__main__':
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    win = SynchroniseWindow()
    win.show()
    app.exec_()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
