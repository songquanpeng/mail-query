import os
import sys
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIntValidator

from query import query
from util import parse


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.directory = os.getcwd().replace("\\", "/") + "/data"
        self.keyword = ""
        self.fileList = []
        self.options_names = ["Subject", "Sender", "Receiver", "Date", "Content",
                              "Attachment filename", "Attachment content"]
        self.options = [True for _ in range(len(self.options_names))]
        self.limit = -1

        self.dirPathEdit = QLineEdit()
        self.searchEdit = QLineEdit()
        self.listWidget = QListWidget()

        self.dirPathEdit.setText(self.directory)
        self.dirPathEdit.setObjectName("directory")
        self.searchEdit.setObjectName("keyword")

        self.dirPathEdit.textChanged.connect(self.on_edit_changed)
        self.dirPathEdit.returnPressed.connect(self.select_dir)
        self.searchEdit.textChanged.connect(self.on_edit_changed)
        self.searchEdit.returnPressed.connect(self.search)
        self.listWidget.itemDoubleClicked.connect(self.open_file)

        self.init_ui()
        self.select_dir()
        self.searchEdit.setFocus()

    def init_ui(self):
        self.resize(1200, 900)
        self.setWindowTitle("hello motherfucker")

        dirPathLabel = QLabel("Directory path:")
        dirBrowseBtn = QPushButton("Browse")

        searchLabel = QLabel("Keyword:")
        searchBtn = QPushButton("Search")

        scopeLabel = QLabel("Search scope:")

        otherLabel = QLabel("Other options:")
        limitLabel = QLabel("Maximum results number:")
        limitEdit = QLineEdit()
        limitEdit.setValidator(QIntValidator())
        limitEdit.setObjectName("limit")
        regexpLabel = QLabel("Regexp")
        regexpCheckbox = QCheckBox()

        dirBrowseBtn.clicked.connect(self.browse_dir)
        searchBtn.clicked.connect(self.search)
        limitEdit.textChanged.connect(self.on_edit_changed)

        otherHBox = QHBoxLayout()
        otherHBox.setSpacing(10)
        otherHBox.addWidget(limitLabel)
        otherHBox.addWidget(limitEdit)
        otherHBox.addSpacing(50)
        otherHBox.addWidget(regexpLabel)
        otherHBox.addWidget(regexpCheckbox)
        otherHBox.addStretch()

        optionsHBox = QHBoxLayout()
        optionsHBox.setSpacing(10)

        for index, name in enumerate(self.options_names):
            checkbox = QCheckBox()
            checkbox.setObjectName(str(index))
            checkbox.stateChanged.connect(self.on_options_changed)
            checkbox.setCheckState(Qt.Checked if self.options[index] else Qt.Unchecked)
            label = QLabel(name)
            optionsHBox.addWidget(label)
            optionsHBox.addWidget(checkbox)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(dirPathLabel, 0, 0)
        grid.addWidget(self.dirPathEdit, 0, 1)
        grid.addWidget(dirBrowseBtn, 0, 2, 1, 1)
        grid.addWidget(searchLabel, 1, 0)
        grid.addWidget(self.searchEdit, 1, 1)
        grid.addWidget(searchBtn, 1, 2)
        grid.addWidget(scopeLabel, 2, 0)
        grid.addItem(optionsHBox, 2, 1, 1, 2)
        grid.addWidget(otherLabel, 3, 0)
        grid.addItem(otherHBox, 3, 1, 1, 2)
        grid.addWidget(self.listWidget, 4, 0, 1, 3)

        self.setLayout(grid)

    def browse_dir(self):
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if directory != "":
            self.directory = directory
            self.dirPathEdit.setText(self.directory)
            self.select_dir()
            self.searchEdit.setFocus()

    def select_dir(self):
        try:
            fileList = []
            for file in os.listdir(self.directory):
                if file.endswith(".eml"):
                    fileList.append(file)
            self.fileList = fileList

            self.listWidget.clear()
            self.listWidget.addItems(self.fileList)
        except OSError as e:
            QMessageBox.critical(self, "Error", e.strerror, QMessageBox.Ok,
                                 QMessageBox.Ok)

    def open_file(self, item):
        path = self.directory + "/" + item.text()
        try:
            os.startfile(path)
        except OSError as e:
            QMessageBox.critical(self, "Error", e.strerror, QMessageBox.Ok,
                                 QMessageBox.Ok)

    def search(self):
        try:
            mails = []
            for file in self.fileList:
                mails.append(parse(self.directory + "/" + file))
            start = time.time()
            index = query(self.keyword, mails, int(self.limit), self.options)
            result = [self.fileList[i] for i in index]
            self.listWidget.clear()
            self.listWidget.addItems(result)
            end = time.time()
            print(index, end - start, "seconds")
        except OSError as e:
            QMessageBox.critical(self, "Error", e.strerror, QMessageBox.Ok,
                                 QMessageBox.Ok)
        except ValueError:
            QMessageBox.critical(self, "Error", "Limit number must be valid integer",
                                 QMessageBox.Ok, QMessageBox.Ok)

    def on_edit_changed(self, text):
        name = self.sender().objectName()
        setattr(self, name, text)

    def on_options_changed(self, check_state):
        options = self.options
        index = int(self.sender().objectName())
        options[index] = bool(check_state)
        setattr(self, "options", options)

    def closeEvent(self, QCloseEvent):
        reply = QMessageBox.question(self, "Message", "Are you sure to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
