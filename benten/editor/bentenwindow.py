"""Provides a view into a CWL component, like a workflow. The view can be of a whole CWL file
or a part of a CWL file, like an in-lined step. Changes to a part of a CWL file are """

import time
import pathlib

from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QLineEdit, QTableView, QWidget
from PySide2.QtGui import QTextCursor, QPainter

from benten.editor.codeeditor import CodeEditor
from benten.editor.processview import ProcessView
from benten.editor.workflowscene import WorkflowScene

import benten.lib as blib
from benten.models.workflow import Workflow


class ProgrammaticEdit:
    def __init__(self, raw_cwl, cursor_line):
        self.raw_cwl = raw_cwl
        self.cursor_line = cursor_line


class ManualEditManager:
    """Each manual edit we do (letter we type) triggers a manual edit. We need to manage
    these calls so they don't overwhelm the system and yet not miss out on the final edit in
    a burst of edits. This manager handles that job effectively."""
    def __init__(self):
        self.burst_window = 1.0
        # We allow upto a <burst_window> pause in typing before parsing the edit
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(int(self.burst_window * 1000))

    def restart_edit_clock(self):
        self.timer.start()


class BentenWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.code_editor: CodeEditor = CodeEditor()
        self.process_view: ProcessView = ProcessView(self)
        self.command_bar = QLineEdit(self)
        self.inbound_conn_table = QTableView(self)
        self.outbound_conn_table = QTableView(self)

        conn_panes = QHBoxLayout()
        conn_panes.addWidget(self.inbound_conn_table)
        conn_panes.addWidget(self.outbound_conn_table)

        horiz_panes = QVBoxLayout()
        horiz_panes.addWidget(self.process_view)
        horiz_panes.addWidget(self.command_bar)
        horiz_panes.addLayout(conn_panes)

        vertical_panes = QHBoxLayout()
        vertical_panes.addLayout(horiz_panes)
        vertical_panes.addWidget(self.code_editor)

        self.setLayout(vertical_panes)

        self.manual_edit_manager = ManualEditManager()
        self.manual_edit_manager.timer.timeout.connect(self.update_from_code)

        self.current_programmatic_edit: ProgrammaticEdit = None

        self.process_to_edit: (Workflow,) = None
        self.process_file_path = None

        self.code_editor.textChanged.connect(self.manual_edit)

    def load(self, path: pathlib.Path):
        # This registers as the first manual edit, but we force the update to happen immediately
        blk = QSignalBlocker(self.code_editor)
        self.process_file_path = path
        self.code_editor.setPlainText(path.open("r").read())
        self.update_from_code()

    @Slot()
    def manual_edit(self):
        """Called whenever the code is changed manually"""
        self.manual_edit_manager.restart_edit_clock()

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
        self.code_editor.update_line_number_area_width(0)  # This is needed so that everything aligns right
        self.code_editor.highlight_current_line()

        self.update_from_code()

    @Slot()
    def update_from_code(self):

        modified_cwl = self.code_editor.toPlainText()

        # todo: check for version and type of CWL document
        self.process_to_edit = \
            Workflow(cwl_doc=blib.yamlify(modified_cwl), path=self.process_file_path)

        scene = WorkflowScene(self)
        scene.set_workflow(self.process_to_edit)
        self.process_view.setScene(scene)
        self.process_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # self.process_view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
        # self.process_view.ensureVisible(-10, -10, 20, 20)
        # self.process_view.show()
