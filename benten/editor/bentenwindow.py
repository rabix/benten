"""Provides a view into a CWL component, like a workflow. The view can be of a whole CWL file
or a part of a CWL file, like an in-lined step. Changes to a part of a CWL file are """

import time

from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, QWidget, QAbstractItemView
from PySide2.QtGui import QTextCursor, QPainter

from benten.editor.codeeditor import CodeEditor
from benten.editor.processview import ProcessView
from benten.editor.workflowscene import WorkflowScene

from benten.editing.cwldoc import CwlDoc
from benten.models.workflow import Workflow

import logging
logger = logging.getLogger(__name__)


class ProgrammaticEdit:
    def __init__(self, raw_cwl, cursor_line):
        self.raw_cwl = raw_cwl
        self.cursor_line = cursor_line


class ManualEditThrottler:
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


class PersistentEditorState:
    """Each edit causes us to update everything. We need to remember some things."""
    def __len__(self):
        self.selected_items: list = None


class BentenWindow(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.code_editor: CodeEditor = CodeEditor()
        self.code_editor.setFixedWidth(350)
        self.process_view: ProcessView = ProcessView(self)
        # self.command_bar = QLineEdit(self)
        self.conn_table = QTableWidget(self)
        self.conn_table.horizontalHeader().setStretchLastSection(True)
        self.conn_table.verticalHeader().setVisible(False)
        self.conn_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.outbound_conn_table = QTableView(self)

        conn_panes = QHBoxLayout()
        conn_panes.addWidget(self.conn_table)
        # conn_panes.addWidget(self.outbound_conn_table)
        conn_panes.setMargin(0)

        horiz_panes = QVBoxLayout()
        horiz_panes.addWidget(self.process_view, 80)
        # horiz_panes.addWidget(self.command_bar)
        horiz_panes.addLayout(conn_panes, 20)
        horiz_panes.setMargin(0)
        horiz_panes.setSpacing(0)

        vertical_panes = QHBoxLayout()
        vertical_panes.addLayout(horiz_panes)
        vertical_panes.addWidget(self.code_editor)
        vertical_panes.setMargin(0)

        self.setLayout(vertical_panes)

        self.manual_edit_throttler = ManualEditThrottler()
        self.manual_edit_throttler.timer.timeout.connect(self.update_from_code)

        self.cwl_doc: CwlDoc = None
        self.process_model: (Workflow,) = None

        # todo: To deprecate and use different mechanism
        self.current_programmatic_edit: ProgrammaticEdit = None

        self.is_active_window = False

        self.code_editor.textChanged.connect(self.manual_edit)

    def set_document(self, cwl_doc):
        # This registers as a manual edit but we wish to skip the throttler
        blk = QSignalBlocker(self.code_editor)
        self.cwl_doc = cwl_doc
        self.code_editor.setPlainText(self.cwl_doc.raw_cwl)
        self.code_editor.update_line_number_area_width(0)
        self.update_from_code()

    def set_active_window(self):
        """To be called whenever we switch tabs to this window. """
        self.is_active_window = True
        self.update_from_code()

    def set_inactive_window(self):
        """To be called whenever we switch away from this window"""
        self.is_active_window = False

    @Slot()
    def manual_edit(self):
        """Called whenever the code is changed manually"""
        self.manual_edit_throttler.restart_edit_clock()

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

        t0 = time.time()

        if not self.is_active_window:
            # Defer updating until we can be seen
            return

        modified_cwl = self.code_editor.toPlainText()
        if self.process_model is not None:
            if self.process_model.cwl_doc.raw_cwl == modified_cwl:
                return

        self.cwl_doc = CwlDoc(raw_cwl=modified_cwl,
                              path=self.cwl_doc.path,
                              inline_path=self.cwl_doc.inline_path)

        # todo: check for version and type of CWL document
        self.process_model = \
            Workflow(cwl_doc=self.cwl_doc)

        scene = WorkflowScene(self)
        scene.selectionChanged.connect(self.something_selected)

        scene.set_workflow(self.process_model)
        self.process_view.setScene(scene)
        self.process_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        t1 = time.time()

        logger.debug("Parsed and displayed workflow in {}s".format(t1 - t0))
        if self.process_model.problems_with_wf:
            logger.warning(self.process_model.problems_with_wf)

        # self.process_view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
        # self.process_view.ensureVisible(-10, -10, 20, 20)
        # self.process_view.show()

    @Slot()
    def something_selected(self):
        items = self.process_view.scene().selectedItems()
        if len(items) == 1:
            info = items[0].data(0)
            if isinstance(info, str):
                if info in ["inputs", "outputs"]:
                    self.highlight_workflow_io(info)
                else:
                    self.highlight_step(info)
            elif isinstance(info, tuple):
                self.highlight_connection_between_nodes(info)

    def highlight_workflow_io(self, info: str):
        pass

    def highlight_step(self, info: str):
        step = self.process_model.steps[info]
        logger.debug("Scroll to line {}".format(step.line[0]))
        self.code_editor.scroll_to(step.line[0])

        inbound_conn = [c for c in self.process_model.connections if c.dst.node_id == info]
        outbound_conn = [c for c in self.process_model.connections if c.src.node_id == info]

        self.populate_connection_table(step.id, [inbound_conn, outbound_conn])

    def highlight_connection_between_nodes(self, info: tuple):
        pass

    def populate_connection_table(self, title, conns: [dict]):
        row, col = 0, 0
        self.conn_table.clear()
        self.conn_table.setColumnCount(1)
        self.conn_table.setRowCount(sum(len(c) for c in conns))
        self.conn_table.setHorizontalHeaderLabels([title])
        for conn_grp in conns:
            for conn in conn_grp:
                item = QTableWidgetItem(str(conn))
                item.setData(Qt.UserRole, conn)  # All other roles try to replace as display text
                self.conn_table.setItem(row, col, item)
                row += 1
