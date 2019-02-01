import sys
import time
import pathlib

from PySide2.QtCore import Qt, QDateTime, QModelIndex, QSignalBlocker, QRect, Qt, QTimeZone, Slot

from PySide2.QtWidgets import QAction, QApplication, QPushButton, QLabel, QHBoxLayout, QVBoxLayout, QHeaderView, \
    QMenuBar, QMainWindow, QLineEdit, QSizePolicy, QTableView, QWidget

from PySide2.QtGui import QTextCursor

from benten.editor.codeeditor import CodeEditor
from benten.editor.processview import ProcessView
import benten.logic.workflow as blwf


class ProgrammaticEdit:
    def __init__(self, raw_cwl, cursor_line):
        self.raw_cwl = raw_cwl
        self.cursor_line = cursor_line


class BentenWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.code_editor: CodeEditor = CodeEditor()
        self.workflow_map: ProcessView = ProcessView(self)
        self.command_bar = QLineEdit(self)
        self.inbound_conn_table = QTableView(self)
        self.outbound_conn_table = QTableView(self)

        conn_panes = QHBoxLayout()
        conn_panes.addWidget(self.inbound_conn_table)
        conn_panes.addWidget(self.outbound_conn_table)

        horiz_panes = QVBoxLayout()
        horiz_panes.addWidget(self.workflow_map)
        horiz_panes.addWidget(self.command_bar)
        horiz_panes.addLayout(conn_panes)

        vertical_panes = QHBoxLayout()
        vertical_panes.addLayout(horiz_panes)
        vertical_panes.addWidget(self.code_editor)

        self.setLayout(vertical_panes)

        self.last_update_time = time.time()
        self.update_interval = 2.0

        self.current_programmatic_edit: ProgrammaticEdit = None

        self.code_editor.textChanged.connect(self.manual_edit)

    def load(self, path: pathlib.Path):

        # This is elegant because it invokes the programmatic edits mechanism (DRY)
        # BUT now the edit history carries the initial blank document
        # self.current_programmatic_edit = ProgrammaticEdit(path.open("r").read(), 0)
        # self.programmatic_edit()

        # So instead we do this directly
        self.code_editor.setPlainText(path.open("r").read())
        self.update_from_code()

    @Slot()
    def manual_edit(self):
        """Called whenever the code is changed manually"""
        if time.time() - self.last_update_time > self.update_interval:
            self.last_update_time = time.time()
            self.update_from_code()

    @Slot()
    def programmatic_edit(self):
        """Called when we have a programmatic edit to execute"""
        # https://doc.qt.io/qt-5/qsignalblocker.html
        blk = QSignalBlocker(self.code_editor)

        # https://programtalk.com/python-examples/PySide2.QtGui.QTextCursor/
        # https://www.qtcentre.org/threads/43268-Setting-Text-in-QPlainTextEdit-without-Clearing-Undo-Redo-History
        doc = self.code_editor.document()
        insert_cursor = QTextCursor(doc)
        insert_cursor.select(QTextCursor.SelectionType.Document)
        insert_cursor.insertText(self.current_programmatic_edit.raw_cwl)

        # https://stackoverflow.com/questions/27036048/how-to-scroll-to-the-specified-line-in-qplaintextedit
        final_cursor = QTextCursor(
            doc.findBlockByLineNumber(self.current_programmatic_edit.cursor_line))
        self.code_editor.setTextCursor(final_cursor)
        self.code_editor.update_line_number_area_width(0) # This is needed so that everything aligns right
        self.code_editor.highlight_current_line()

        self.update_from_code()

    def update_from_code(self):
        print("Bing!")


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Benten")

        # Menu
        menu = self.menuBar()
        file_menu = menu.addMenu("File")

        # Exit QAction
        exit_action = QAction("&Exit", self)
        #exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.exit_app)
        file_menu.addAction(exit_action)

        # Status Bar
        self.status = self.statusBar()
        self.status.showMessage("Ready")

        # Window dimensions
        # geometry = app.desktop().availableGeometry(self)
        # self.setFixedSize(geometry.width() * 0.8, geometry.height() * 0.7)

        self.benten_window = BentenWindow()
        self.setCentralWidget(self.benten_window)
        self.benten_window.code_editor.setFocus()

        self.centralWidget().load(pathlib.Path("/Users/kghose/Work/code/benten/tests/cwl/sbg/salmon.cwl"))

    @Slot()
    def exit_app(self, checked):
        sys.exit()


def main():
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
