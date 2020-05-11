import sys
from PyQt5.QtWidgets import (QApplication, QWidget,
                             QPushButton, QMessageBox,
                             QMainWindow, QLineEdit,
                             QTextBrowser, QListView,
                             QFileDialog, QLabel
                             )
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class App(QWidget):
    def __init__(self):
        # noinspection PyArgumentList
        super().__init__()
        self.directory = ""
        self.keyword = ""

        self.searchEdit = QLineEdit()
        self.listView = QListView()
        self.dirPathEdit = QLineEdit()

        self.init_ui()

    def init_ui(self):
        self.resize(800, 600)
        self.setWindowTitle("hello motherfucker")

        searchLabel = QLabel("Keyword:")
        searchBtn = QPushButton("Search")
        dirPathLabel = QLabel("Directory path:")
        dirBrowseBtn = QPushButton("Browse")
        dirSelectBtn = QPushButton("Select")

        dirBrowseBtn.clicked.connect(self.browse_file)

        grid = QGridLayout()
        grid.setSpacing(10)
        grid.addWidget(dirPathLabel, 0, 0)
        grid.addWidget(self.dirPathEdit, 0, 1)
        grid.addWidget(dirBrowseBtn, 0, 2, 1, 1)
        grid.addWidget(dirSelectBtn, 0, 3)
        grid.addWidget(searchLabel, 1, 0)
        grid.addWidget(self.searchEdit, 1, 1, 1, 2)
        grid.addWidget(searchBtn, 1, 3)
        grid.addWidget(self.listView, 2, 0, 1, 4)

        self.setLayout(grid)

    def browse_file(self):
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.dirPathEdit.setText(self.directory)

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
