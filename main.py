import os
import sys
import time

from PyQt5.QtWidgets import QLineEdit, QWidget, QListWidget, QLabel, QPushButton, QCheckBox, \
    QHBoxLayout, QGridLayout, QFileDialog, QMessageBox, QApplication, QStatusBar, QMainWindow
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIntValidator

from query import query
from util import parse


class LoadThread(QThread):
    trigger = pyqtSignal(str)

    def __init__(self, directory):
        super(LoadThread, self).__init__()
        self.directory = directory
        self.fileList = []
        self.mails = []

    def run(self):
        try:
            fileList = []
            for file in os.listdir(self.directory):
                if file.endswith(".eml"):
                    fileList.append(file)
            self.fileList = fileList

            mails = []
            for file in self.fileList:
                mails.append(parse(self.directory + "/" + file))
            self.mails = mails

            self.trigger.emit("success")
        except OSError as e:
            self.trigger.emit(e.strerror)


class SearchThread(QThread):
    trigger = pyqtSignal()

    def __init__(self, keyword, mails, limit, options):
        super(SearchThread, self).__init__()
        self.index = []
        self.keyword = keyword
        self.mails = mails
        self.limit = limit
        self.options = options

    def run(self):
        self.index = query(self.keyword, self.mails, self.limit, self.options)
        self.trigger.emit()


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.load_thread = None
        self.search_thread = None

        self.directory = os.getcwd().replace("\\", "/") + "/data"
        self.keyword = ""
        self.fileList = []
        self.mails = []
        self.options_names = ["Subject", "Sender", "Receiver", "Date", "Content",
                              "Attachment filename", "Attachment content"]
        self.options = [True for _ in range(len(self.options_names))]
        self.limit = -1
        self.timer = time.time()

        self.dirPathEdit = QLineEdit()
        self.searchEdit = QLineEdit()
        self.searchBtn = QPushButton("Search")
        self.listWidget = QListWidget()
        self.statusBar = QStatusBar()

        self.dirPathEdit.setText(self.directory)
        self.dirPathEdit.setObjectName("directory")
        self.searchEdit.setObjectName("keyword")

        self.dirPathEdit.textChanged.connect(self.on_edit_changed)
        self.dirPathEdit.returnPressed.connect(self.select_dir)
        self.searchEdit.textChanged.connect(self.on_edit_changed)
        self.searchEdit.returnPressed.connect(self.search)
        self.searchBtn.clicked.connect(self.search)
        self.listWidget.itemDoubleClicked.connect(self.open_file)

        self.init_ui()
        self.select_dir()
        self.searchEdit.setFocus()

    def init_ui(self):
        dirPathLabel = QLabel("Directory path:")
        dirBrowseBtn = QPushButton("Browse")

        searchLabel = QLabel("Keyword:")

        scopeLabel = QLabel("Search scope:")

        otherLabel = QLabel("Other options:")
        limitLabel = QLabel("Maximum results number:")
        limitEdit = QLineEdit()
        limitEdit.setValidator(QIntValidator())
        limitEdit.setObjectName("limit")
        regexpLabel = QLabel("Regexp")
        regexpCheckbox = QCheckBox()

        dirBrowseBtn.clicked.connect(self.browse_dir)
        limitEdit.textChanged.connect(self.on_edit_changed)
        limitEdit.setText("-1")

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
        grid.addWidget(self.searchBtn, 1, 2)
        grid.addWidget(scopeLabel, 2, 0)
        grid.addItem(optionsHBox, 2, 1, 1, 2)
        grid.addWidget(otherLabel, 3, 0)
        grid.addItem(otherHBox, 3, 1, 1, 2)
        grid.addWidget(self.listWidget, 4, 0, 1, 3)
        grid.addWidget(self.statusBar, 5, 0, 1, 3)

        self.setLayout(grid)

    def browse_dir(self):
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if directory != "":
            self.directory = directory
            self.dirPathEdit.setText(self.directory)
            self.select_dir()
            self.searchEdit.setFocus()

    def select_dir(self):
        self.load_thread = LoadThread(self.directory)
        self.load_thread.trigger.connect(self.on_load_thread_returned)
        self.timer = time.time()
        self.load_thread.start()

    def open_file(self, item):
        path = self.directory + "/" + item.text()
        try:
            os.startfile(path)
        except OSError as e:
            QMessageBox.critical(self, "Error", e.strerror, QMessageBox.Ok,
                                 QMessageBox.Ok)

    def search(self):
        try:
            self.search_thread = SearchThread(self.keyword, self.mails, int(self.limit),
                                              self.options)
            self.search_thread.trigger.connect(self.on_search_thread_returned)
            self.statusBar.showMessage("Processing query...")
            self.searchBtn.setEnabled(False)
            self.timer = time.time()
            self.search_thread.start()
        except ValueError:
            QMessageBox.critical(self, "Error", "Limit number must be valid integer.",
                                 QMessageBox.Ok, QMessageBox.Ok)

    def on_load_thread_returned(self, message):
        if message == "success":
            self.fileList = self.load_thread.fileList
            self.mails = self.load_thread.mails
            if not len(self.mails):
                self.statusBar.showMessage("No eml file detected in given directory.")
            else:
                used_time = time.time() - self.timer
                self.statusBar.showMessage("Loaded done in " + str(used_time) + " seconds.")
            self.listWidget.clear()
            self.listWidget.addItems(self.fileList)
        else:
            QMessageBox.critical(self, "Error", message, QMessageBox.Ok, QMessageBox.Ok)

    def on_search_thread_returned(self):
        used_time = time.time() - self.timer
        index = self.search_thread.index
        result = [self.fileList[i] for i in index]
        self.listWidget.clear()
        self.listWidget.addItems(result)
        self.searchBtn.setText("Search")
        self.searchBtn.setEnabled(True)
        self.statusBar.showMessage("Got " + str(len(result)) + " results, query done in "
                                   + str(used_time) + " seconds.")

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


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.resize(1200, 900)
        self.setWindowTitle("hello motherfucker")

        self.setCentralWidget(App())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
