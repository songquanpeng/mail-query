import os
import sys
import time
import glob
import webbrowser
from multiprocessing import Process, ProcessError

from PyQt5.QtWidgets import QLineEdit, QWidget, QListWidget, QLabel, QPushButton, QCheckBox, \
    QHBoxLayout, QGridLayout, QFileDialog, QMessageBox, QApplication, QStatusBar, QMainWindow, \
    QAction, QTextBrowser, QListWidgetItem
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIntValidator, QIcon

from utils.database import init, insert, query, create_connection
from utils.utils import parse
from server import serve, host, port


class LoadThread(QThread):
    trigger = pyqtSignal(str)

    def __init__(self, files):
        super(LoadThread, self).__init__()
        self.fileList = []
        self.files = files

    def run(self):
        conn = create_connection()
        try:
            files = self.files
            if type(files) is str:
                fileList = glob.glob(f"{files}/*.eml")
            elif type(files) is list:
                fileList = files
            else:
                self.trigger.emit("Load files failed.")
                return
            self.fileList = fileList
            for file in self.fileList:
                mail = parse(file)
                insert(mail, conn)
            self.trigger.emit("success")
        except OSError as e:
            self.trigger.emit(e.strerror)
        finally:
            conn.commit()


class SearchThread(QThread):
    trigger = pyqtSignal()

    def __init__(self, keyword, limit, options):
        super(SearchThread, self).__init__()
        self.result = []
        self.keyword = keyword
        self.limit = limit
        self.options = options

    def run(self):
        conn = create_connection()
        self.result = query(self.keyword, limit=self.limit, option=self.options, more=True,
                            conn=conn, full_content=True)
        self.trigger.emit()


class App(QWidget):
    def __init__(self):
        super().__init__()

        self.load_thread = None
        self.search_thread = None

        self.keyword = ""
        self.options_names = ["Subject", "Sender", "Receiver", "Date", "Content",
                              "Attachment filename", "Attachment content"]
        self.options = [True for _ in range(len(self.options_names))]
        self.limit = -1
        self.timer = time.time()

        self.searchEdit = QLineEdit()
        self.searchBtn = QPushButton("Search")
        self.listWidget = QListWidget()
        self.textBrowser = QTextBrowser();
        self.statusBar = QStatusBar()

        self.searchEdit.setObjectName("keyword")
        self.searchEdit.setPlaceholderText("Input keyword to search...")

        self.searchEdit.textChanged.connect(self.on_edit_changed)
        self.searchEdit.returnPressed.connect(self.search)
        self.searchBtn.clicked.connect(self.search)
        self.listWidget.itemClicked.connect(self.on_list_item_clicked)
        self.listWidget.itemDoubleClicked.connect(self.on_list_item_double_clicked)

        self.init_ui()
        self.statusBar.showMessage("Input keyword to query.")
        self.searchEdit.setFocus()

    def init_ui(self):

        searchLabel = QLabel("Keyword:")

        scopeLabel = QLabel("Search scope:")

        otherLabel = QLabel("Other options:")
        limitLabel = QLabel("Maximum results number:")
        limitEdit = QLineEdit()

        limitEdit.setValidator(QIntValidator())
        limitEdit.setObjectName("limit")
        limitEdit.textChanged.connect(self.on_edit_changed)
        limitEdit.setText("-1")

        otherHBox = QHBoxLayout()
        otherHBox.setSpacing(10)
        otherHBox.addWidget(limitLabel)
        otherHBox.addWidget(limitEdit)
        otherHBox.addStretch()

        optionsHBox = QHBoxLayout()
        optionsHBox.setSpacing(10)

        viewHBox = QHBoxLayout()
        viewHBox.setSpacing(10)
        viewHBox.addWidget(self.listWidget)
        viewHBox.addWidget(self.textBrowser)

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
        grid.addWidget(searchLabel, 1, 0)
        grid.addWidget(self.searchEdit, 1, 1)
        grid.addWidget(self.searchBtn, 1, 2)
        grid.addWidget(scopeLabel, 2, 0)
        grid.addItem(optionsHBox, 2, 1, 1, 2)
        grid.addWidget(otherLabel, 3, 0)
        grid.addItem(otherHBox, 3, 1, 1, 2)
        grid.addItem(viewHBox, 4, 0, 1, 3)
        grid.addWidget(self.statusBar, 5, 0, 1, 3)

        self.setLayout(grid)

    def browse_files(self):
        fileList = QFileDialog().getOpenFileNames(self, "Select .eml files", "",
                                                  "E-mail files (*.eml)")[0]
        if len(fileList) != 0:
            self.load_files(fileList)
        else:
            self.statusBar.showMessage("Add files canceled.")

    def browse_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory != "":
            self.load_files(directory)
        else:
            self.statusBar.showMessage("Add directory canceled.")

    def load_files(self, files):
        self.statusBar.showMessage("Loading, please hold on...")
        self.load_thread = LoadThread(files)
        self.load_thread.trigger.connect(self.on_load_thread_returned)
        self.timer = time.time()
        self.load_thread.start()

    def on_list_item_clicked(self, item: QListWidgetItem):
        mail = item.data(Qt.UserRole)
        subject = mail['subject']
        sender = mail['sender']
        receiver = mail['receiver']
        date = mail['date']
        content = mail['content']

        preview_text = f"<h1>{subject}</h1><p>date: {date}</p><p>sender: {sender}</p>" \
                       f"<p>receiver: {receiver}</p>{content if content else '(empty content)'}"
        self.textBrowser.setText(preview_text)

    def on_list_item_double_clicked(self, item: QListWidgetItem):
        try:
            path = item.data(Qt.UserRole)['path']
            os.startfile(path)
        except OSError as e:
            QMessageBox.critical(self, "Error", e.strerror, QMessageBox.Ok,
                                 QMessageBox.Ok)

    def search(self):
        try:
            self.search_thread = SearchThread(self.keyword, int(self.limit), self.options)
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
            fileList = self.load_thread.fileList
            if not len(fileList):
                self.statusBar.showMessage("No eml file detected in given directory.")
            else:
                used_time = time.time() - self.timer
                self.statusBar.showMessage("Loaded " + str(len(fileList)) + " files, done in " +
                                           str(used_time) + " seconds.")
            self.listWidget.clear()
            self.listWidget.addItems(fileList)
        else:
            QMessageBox.critical(self, "Error", message, QMessageBox.Ok, QMessageBox.Ok)

    def on_search_thread_returned(self):
        used_time = time.time() - self.timer
        mails = self.search_thread.result

        self.listWidget.clear()
        for mail in mails:
            name = os.path.basename(mail["path"])
            name = os.path.splitext(name)[0]

            item = QListWidgetItem()
            item.setData(Qt.UserRole, mail)
            item.setText(name)
            self.listWidget.addItem(item)

        self.searchBtn.setText("Search")
        self.searchBtn.setEnabled(True)
        self.statusBar.showMessage("Got " + str(len(mails)) + " results, query done in "
                                   + str(used_time) + " seconds.")

    def on_edit_changed(self, text):
        name = self.sender().objectName()
        setattr(self, name, text)

    def on_options_changed(self, check_state):
        options = self.options
        index = int(self.sender().objectName())
        options[index] = bool(check_state)
        setattr(self, "options", options)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.app = App()

        self.server_process = None

        self.startServerAction = QAction("&Start server", self)
        self.stopServerAction = QAction("&Stop server", self)
        self.stopServerAction.setEnabled(False)

        self.setCentralWidget(self.app)
        self.init_ui()

    def init_ui(self):
        self.resize(1200, 900)
        self.setWindowTitle("Quick Mail Query")
        self.setWindowIcon(QIcon("./static/icon.png"))

        addFilesAction = QAction("Add &files", self)
        addDirAction = QAction("Add &directory", self)
        helpAction = QAction("&Help", self)
        aboutAction = QAction("&About", self)

        addFilesAction.triggered.connect(self.app.browse_files)
        addDirAction.triggered.connect(self.app.browse_dir)
        self.startServerAction.triggered.connect(self.start_server)
        self.stopServerAction.triggered.connect(self.stop_server)
        helpAction.triggered.connect(self.show_help)
        aboutAction.triggered.connect(self.show_about)

        menuBar = self.menuBar()
        fileMenu = menuBar.addMenu('&File')
        fileMenu.addAction(addFilesAction)
        fileMenu.addAction(addDirAction)

        serverMenu = menuBar.addMenu("&Server")
        serverMenu.addAction(self.startServerAction)
        serverMenu.addAction(self.stopServerAction)

        aboutMenu = menuBar.addMenu('&About')
        aboutMenu.addAction(helpAction)
        aboutMenu.addSeparator()
        aboutMenu.addAction(aboutAction)

    def start_server(self):
        try:
            self.server_process = Process(target=serve, daemon=True)
            self.server_process.start()
        except ProcessError:
            self.app.statusBar.showMessage("Failed to create new process for server.(ProcessError)")
        except ValueError:
            self.app.statusBar.showMessage("Failed to create new process for server.(ValueError)")
        else:
            self.startServerAction.setEnabled(False)
            self.stopServerAction.setEnabled(True)

            url = "%s://%s:%d" % ("http", host, port)
            self.app.statusBar.showMessage("Server started and listening on %s" % url)
            webbrowser.open(url, new=2)

    def stop_server(self):
        if self.server_process is not None:
            try:
                self.server_process.terminate()
                time.sleep(0.1)
                self.server_process.close()
            except ProcessError:
                self.app.statusBar.showMessage("Failed to stop the server process.(ProcessError)")
            except ValueError:
                self.app.statusBar.showMessage("Cannot close process. Please try again.("
                                               "ValueError)")
            else:
                self.startServerAction.setEnabled(True)
                self.stopServerAction.setEnabled(False)
                self.app.statusBar.showMessage("Server stopped.")

    def show_help(self):
        QMessageBox.information(self, "Help",
                                'Before querying, you need to import the files to the system '
                                'first: click the "File" menu, select eml files or the directory '
                                'that contains eml files.\n'
                                , QMessageBox.Ok)

    def show_about(self):
        QMessageBox.information(self, "About", "<h3>Quick Mail Query</h3>"
                                               "<a href='https://github.com/"
                                               "songquanpeng/mail-query'>Github Repo</a>",
                                QMessageBox.Close)

    def closeEvent(self, QCloseEvent):
        reply = QMessageBox.question(self, "Message", "Are you sure to quit?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.stop_server()
            QCloseEvent.accept()
        else:
            QCloseEvent.ignore()


if __name__ == '__main__':
    init()
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
