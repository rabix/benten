import sys
import time
import pathlib

from PySide2.QtCore import Qt, QDateTime, QModelIndex, QSignalBlocker, QRect, Qt, QTimer, Slot

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


class ManualEditManager:
    """Each manual edit we do (letter we type) triggers a manual edit. We need to manage
    these calls so they don't overwhelm the system and yet not miss out on the final edit in
    a burst of edits. This manager handles that job effectively"""
    def __init__(self):
        self.update_interval = 2.0
        self.last_update_time = 0.0
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(int(self.update_interval * 1000))

    def pass_on_edit(self):
        if time.time() - self.last_update_time > self.update_interval:
            self.timer.stop()
            self.last_update_time = time.time()
            return True
        else:
            self.timer.start()
            # Remember to register this edit in case it's the last one in a burst
            return False


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

        self.manual_edit_manager = ManualEditManager()
        self.manual_edit_manager.timer.timeout.connect(self.manual_edit)

        self.current_programmatic_edit: ProgrammaticEdit = None

        self.code_editor.textChanged.connect(self.manual_edit)

    def load(self, path: pathlib.Path):
        # This registers as the first manual edit
        self.code_editor.setPlainText(path.open("r").read())

    @Slot()
    def manual_edit(self):
        """Called whenever the code is changed manually"""
        if self.manual_edit_manager.pass_on_edit():
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
