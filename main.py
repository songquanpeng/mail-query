import sys, os, subprocess
from PyQt5.QtWidgets import (QApplication, QWidget,
                             QPushButton, QMessageBox,
                             QMainWindow, QLineEdit,
                             QTextBrowser, QListWidget,
                             QFileDialog, QLabel
                             )
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.directory = ""
        self.keyword = ""

        self.searchEdit = QLineEdit()
        self.listWidget = QListWidget()
        self.dirPathEdit = QLineEdit()

        self.dirPathEdit.textChanged.connect(self.on_dir_changed)
        self.listWidget.itemClicked.connect(self.open_file)

        self.init_ui()

    def init_ui(self):
        self.resize(800, 600)
        self.setWindowTitle("hello motherfucker")

        searchLabel = QLabel("Keyword:")
        searchBtn = QPushButton("Search")
        dirPathLabel = QLabel("Directory path:")
        dirBrowseBtn = QPushButton("Browse")
        dirSelectBtn = QPushButton("Select")

        dirBrowseBtn.clicked.connect(self.browse_dir)
        dirSelectBtn.clicked.connect(self.select_dir)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(dirPathLabel, 0, 0)
        grid.addWidget(self.dirPathEdit, 0, 1)
        grid.addWidget(dirBrowseBtn, 0, 2, 1, 1)
        grid.addWidget(dirSelectBtn, 0, 3)
        grid.addWidget(searchLabel, 1, 0)
        grid.addWidget(self.searchEdit, 1, 1, 1, 2)
        grid.addWidget(searchBtn, 1, 3)
        grid.addWidget(self.listWidget, 2, 0, 1, 4)

        self.setLayout(grid)

    def browse_dir(self):
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.dirPathEdit.setText(self.directory)

    def select_dir(self):
        directory = self.directory
        try:
            dirList = os.listdir(directory)
            self.listWidget.clear()
            self.listWidget.addItems(dirList)
        except OSError as e:
            QMessageBox.critical(self, "Error", e.strerror, QMessageBox.Ok, QMessageBox.Ok)

    def open_file(self, item):
        path = self.directory + "/" + item.text()
        try:
            os.startfile(path)
        except OSError as e:
            QMessageBox.critical(self, "Error", e.strerror, QMessageBox.Ok, QMessageBox.Ok)

    def on_dir_changed(self, text):
        self.directory = text

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
