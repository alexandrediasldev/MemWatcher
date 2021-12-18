# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import copy
import sys
import ctypes
import threading

from PyQt5.QtGui import QColor, QPixmap, QIcon
from PyQt5.uic.properties import QtGui
from mem_edit import Process
from time import sleep

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QHBoxLayout, QSpinBox, QLabel, QListWidget, \
    QVBoxLayout


def getProcess():
    pid = Process.get_pid_by_name("Game.exe")
    p = Process.open_process(pid)
    return p


def getStruct(initial_value):
    class MyStruct(ctypes.Structure):
        _fields_ = [
            ('map_id', ctypes.c_int),
        ]

        def change_id(self, value):
            self.map_id = value

        def get_cvalue(self):
            return ctypes.c_int(self.map_id)

    s = MyStruct()
    s.map_id = initial_value
    return s


class MyThread(threading.Thread):
    def __init__(self, function):
        threading.Thread.__init__(self)
        self.function = function

    def run(self):
        # target function of the thread class
        try:
            self.function()
        finally:
            print('Synchronisation killed')

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


class MemoryScanner:
    def __init__(self, s, found_function, reset_function, update_adress_function, update_value_function):
        self.data = s
        self.addrs = []
        self.th = None
        self.found_function = found_function
        self.reset_function = reset_function
        self.update_adress_function = update_adress_function
        self.update_value_function = update_value_function

    def hardcodingValue(self, value):
        self.addrs = [int(value, 0)]

    def set_memory_value(self, value):
        self.data.change_id(value)

    def searchFirstMap(self):
        with getProcess() as p:
            self.addrs = p.search_all_memory(self.data.get_cvalue())
        self.update_adress_function()

    def searchMapId(self):
        p = getProcess()
        with getProcess() as p:
            self.addrs = p.search_addresses(self.addrs, self.data.get_cvalue())

    def searchMapIdMultiple(self, num):
        # if (len(self.addrs) == 1):
        #    print(hex(self.addrs[0]))
        #    self.startSynchronising()
        if (len(self.addrs) == 0):
            self.searchFirstMap()
        else:
            for i in range(num):
                self.searchMapId()
            self.update_adress_function()
            if (len(self.addrs) == 1):
                # self.searchMapIdMultiple(1)
                print(hex(self.addrs[0]))
                self.startSynchronising()
        self.update_adress_function()

    def startSynchronising(self):
        self.stopSynchronising()
        self.th = MyThread(self.print_loop)
        self.th.start()
        self.found_function()

    def stopSynchronising(self):
        if (self.th):
            self.th.raise_exception()
            self.th = None
        self.reset_function()

    def resetSearch(self):
        self.stopSynchronising()
        self.addrs = []
        self.update_adress_function()

    def print_loop(self):
        with getProcess() as p:
            val = ctypes.c_int(99999)
            while len(self.addrs) == 1:
                prev = val.value
                p.read_memory(self.addrs[0], val)
                if (prev != val.value):
                    self.update_value_function(val.value)
                sleep(1)


class ColorLabel(QLabel):
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        self.setStyleSheet("background-color: rgb(220, 20, 60)")

    def set_green(self):
        self.setStyleSheet("background-color: rgb(50, 205, 50)")

    def set_red(self):
        self.setStyleSheet("background-color: rgb(220, 20, 60)")


class SynchroniseWindow(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Synchronisation window")
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.create_widgets()

        s = getStruct(15)

        self.list_widget.clicked.connect(lambda: (self.scanner.hardcodingValue(self.list_widget.currentItem().text()),
                                                  self.scanner.startSynchronising()))

        self.scanner = MemoryScanner(s,
                                     lambda: (self.set_synchronise_on()),
                                     lambda: (self.set_synchronise_off()),
                                     lambda: (self.manage_adress()),
                                     lambda val: (self.label_current_map.setText(str((val - 1) // 2)),
                                                  print(hex(self.scanner.addrs[0]) + ": map: " + str((val - 1) // 2))))

        self.scan.clicked.connect(
            lambda: (
            self.scanner.set_memory_value(2 * int(self.lineEdit.value()) + 1), self.scanner.searchMapIdMultiple(3)))

        self.stopSynchronise.clicked.connect(
            lambda: (self.scanner.stopSynchronising(), self.label_current_map.setText("?")))
        self.reset.clicked.connect(lambda: (
        self.scanner.resetSearch(), self.label_current_map.setText("?"), self.label_adress_number.setText("?")))
        self.save.clicked.connect(lambda: (self.save_synchronisation()))

        self.add_widgets()

    def create_widgets(self):
        self.label_indicator = ColorLabel()

        self.label_current_map = QLabel("?")
        self.label_adress_number = QLabel("0")
        self.scan = QPushButton("Scan")
        self.stopSynchronise = QPushButton("Stop Synchronising")
        self.reset = QPushButton("Reset")
        self.save = QPushButton("Save Synchronisation")
        self.lineEdit = QSpinBox()
        self.list_widget = QListWidget()

        self.lineEdit.setMinimum(1)
        self.lineEdit.setMaximum(9998)
        self.list_widget.setMaximumSize(150, 100)
        self.set_synchronise_off()

    def add_widgets(self):
        left_vlayout = QVBoxLayout()
        self.layout.addLayout(left_vlayout)
        left_vlayout.addWidget(self.save)
        left_vlayout.addWidget(self.stopSynchronise)

        bottom_left_hlayout1 = QHBoxLayout()
        left_vlayout.addLayout(bottom_left_hlayout1)
        bottom_left_hlayout1.addWidget(QLabel("Current value:"))
        bottom_left_hlayout1.addWidget(self.label_current_map)

        bottom_left_hlayout2 = QHBoxLayout()
        left_vlayout.addLayout(bottom_left_hlayout2)
        bottom_left_hlayout2.addWidget(QLabel("Adresses found:"))
        bottom_left_hlayout2.addWidget(self.label_adress_number)

        self.layout.addWidget(self.list_widget)
        self.layout.addWidget(self.label_indicator)

        right_vlayout = QVBoxLayout()

        self.layout.addLayout(right_vlayout)

        right_vlayout.addWidget(self.reset)
        right_vlayout.addWidget(self.scan)
        right_vlayout.addWidget(self.lineEdit)

    def manage_adress(self):
        l = len(self.scanner.addrs)
        self.label_adress_number.setText(str(l))
        if (l < 10):
            self.list_widget.clear()
            for a in self.scanner.addrs:
                item = str(hex(a))
                self.list_widget.addItem(item)

    def set_synchronise_on(self):
        self.label_indicator.set_green()
        self.save.setEnabled(True)
        self.stopSynchronise.setEnabled(True)
        #self.scan.setEnabled(False)

    def set_synchronise_off(self):
        self.label_indicator.set_red()
        self.save.setEnabled(False)
        self.stopSynchronise.setEnabled(False)
        #self.scan.setEnabled(True)

    def save_synchronisation(self):
        l = len(self.scanner.addrs)
        print(l)
        if (l == 1):
            self.list_widget.clear()
            item = str(hex(self.scanner.addrs[0]))
            self.list_widget.addItem(item)
            self.label_adress_number.setText(str(l))


if __name__ == '__main__':
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
    win = SynchroniseWindow()
    win.show()
    app.exec_()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
