from PyQt5.QtWidgets import  QWidget, QPushButton, QLineEdit, QHBoxLayout, QSpinBox, QLabel, QListWidget, \
    QVBoxLayout

from memory_scanner import MemoryScanner, getStruct


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
                                     lambda: (self.process_name.text()),
                                     lambda: (self.set_synchronise_on()),
                                     lambda: (self.set_synchronise_off()),
                                     lambda: (self.manage_adress()),
                                     lambda val: (self.label_current_map.setText(str((val - 1) // 2)),
                                                  print(hex(self.scanner.addrs[0]) + ": map: " + str((val - 1) // 2))))

        self.scan.clicked.connect(
            lambda: (
                self.scanner.set_memory_value(2 * int(self.line_edit.value()) + 1), self.scanner.searchMapIdMultiple(3)))

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
        self.process_name = QLineEdit("Game.exe")
        self.line_edit = QSpinBox()
        self.list_widget = QListWidget()

        self.line_edit.setMinimum(1)
        self.line_edit.setMaximum(9998)
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

        right_vlayout.addWidget(self.process_name)
        right_vlayout.addWidget(self.reset)
        right_vlayout.addWidget(self.scan)
        right_vlayout.addWidget(self.line_edit)

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


