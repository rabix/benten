"""Provides a view into a CWL component, like a workflow. The view can be of a whole CWL file
or a part of a CWL file, like an in-lined step."""

import time

from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot, Signal
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QSplitter, QTableWidget, QTableWidgetItem, QWidget, \
    QAbstractItemView, QGraphicsSceneMouseEvent, QTabWidget, QComboBox
from PySide2.QtGui import QTextCursor, QPainter, QFont

from .codeeditor.editor import CodeEditor
from .processview import ProcessView
from .command.commandwidget import CommandWidget
from .unkscene import UnkScene
from .toolscene import ToolScene
from .workflowscene import WorkflowScene

from ..sbg.sbgcwldoc import SBGCwlDoc
from ..models.unk import Unk
from ..models.tool import Tool
from ..models.workflow import Workflow, special_id_for_inputs, special_id_for_outputs, special_ids_for_io

import logging

logger = logging.getLogger(__name__)


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

    def flush(self):
        if self.timer.isActive():
            self.timer.stop()
            self.timer.timeout.emit()


class PersistentEditorState:
    """Each edit causes us to update everything. We need to remember some things."""

    def __len__(self):
        self.selected_items: list = None


class BentenWindow(QWidget):

    scene_double_clicked = Signal(object)
    edit_registered = Signal(object)

    def __init__(self, benten_main_window):
        QWidget.__init__(self)

        self.bmw = benten_main_window

        self.code_editor: CodeEditor = self._setup_code_editor()
        self.navbar = self._setup_navbar()
        self.process_view: ProcessView = ProcessView(None)
        self.utility_tab_widget, self.command_window, self.conn_table \
            = self._setup_utility_tab()
        self._setup_panes()

        self.manual_edit_throttler = ManualEditThrottler()
        self.manual_edit_throttler.timer.timeout.connect(self.manual_edit)

        self.cwl_doc: SBGCwlDoc = None
        self.step_id = None
        self.process_model: (Workflow,) = None

        self.is_active_window = False

    def _setup_code_editor(self):
        ce = CodeEditor(IndentUsingSpaces=True)
        ce.setFont(QFont("Menlo,11,-1,5,50,0,0,0,0,0,Regular"))
        ce.textChanged.connect(self.user_still_typing)
        return ce

    def _setup_navbar(self):
        navbar = QComboBox()
        navbar.activated[str].connect(self.highlight)
        return navbar

    def _setup_utility_tab(self):
        utility_tab_widget = QTabWidget()

        command_window = CommandWidget(self)

        conn_table = QTableWidget()
        conn_table.horizontalHeader().setStretchLastSection(True)
        conn_table.verticalHeader().setVisible(False)
        conn_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        conn_table.cellClicked.connect(self.connection_clicked)

        utility_tab_widget.addTab(command_window, "CMD")
        utility_tab_widget.addTab(conn_table, "Connections")

        return utility_tab_widget, command_window, conn_table

    def _setup_panes(self):
        left_pane = QSplitter()
        left_pane.setHandleWidth(1)
        left_pane.setOrientation(Qt.Vertical)
        left_pane.addWidget(self.process_view)
        left_pane.addWidget(self.utility_tab_widget)
        left_pane.setStretchFactor(0, 3)
        left_pane.setStretchFactor(1, 1)

        right_pane = QVBoxLayout()
        right_pane.addWidget(self.navbar)
        right_pane.addWidget(self.code_editor)
        right_pane.setMargin(0)
        right_pane.setSpacing(0)
        _right_pane = QWidget()
        _right_pane.setLayout(right_pane)

        main_pane = QSplitter(self)
        main_pane.setHandleWidth(1)
        main_pane.addWidget(left_pane)
        main_pane.addWidget(_right_pane)
        main_pane.setStretchFactor(0, 5)
        main_pane.setStretchFactor(1, 3)

        # If we don't put all this in a layout and set zero margin QT puts us in a tiny box within
        # the window
        layout = QHBoxLayout()
        layout.setMargin(0)
        layout.addWidget(main_pane)
        self.setLayout(layout)

    def set_document(self, cwl_doc):
        # This registers as a manual edit but we wish to skip the throttler
        blk = QSignalBlocker(self.code_editor)
        self.cwl_doc = cwl_doc
        self.code_editor.set_text(self.cwl_doc.raw_cwl)

    def set_active_window(self):
        """To be called whenever we switch tabs to this window. """
        self.is_active_window = True
        self.update_from_code()
        self.code_editor.setFocus()
        # When we switch back and forth, we expect to be able to see the editor cursor = focus

    def set_inactive_window(self):
        """To be called whenever we switch away from this window"""
        self.manual_edit_throttler.flush()
        self.is_active_window = False

    @Slot()
    def user_still_typing(self):
        """Called whenever the editor contents are changed. We restrict this to actual typing."""
        logger.debug("User typing ...")
        self.manual_edit_throttler.restart_edit_clock()

    @Slot()
    def manual_edit(self):
        """Called when the user is done with their burst of typing, or we switch away from this tab"""
        logger.debug("Registering manual edit ...")
        self.update_from_code()
        self.edit_registered.emit(self.cwl_doc)  # Meant to tell document manager about the manual edit

    @Slot()
    def programmatic_edit(self):
        """Called when we have executed a programmatic edit"""
        logger.debug("Registering programmatic edit ...")
        self.update_from_code()
        self.edit_registered.emit(self.cwl_doc)  # Meant to tell document manager about the manual edit

    # This only happens when we are in focus and the code has changed
    # It is only here that we do the (semi)expensive parsing computation
    @Slot()
    def update_from_code(self):

        if not self.is_active_window:
            # Defer updating until we can be seen
            return

        modified_cwl = self.code_editor.toPlainText()
        if self.process_model is not None:
            if self.process_model.cwl_doc.raw_cwl == modified_cwl:
                logger.debug("Update asked for, but code hasn't changed.")
                return

        t0 = time.time()

        self.cwl_doc = SBGCwlDoc(raw_cwl=modified_cwl,
                                 path=self.cwl_doc.path,
                                 inline_path=self.cwl_doc.inline_path,
                                 api=self.bmw.api)
        self.cwl_doc.compute_cwl_dict()

        pt = self.cwl_doc.process_type()
        t1 = time.time()

        old_transform = None
        if pt == "Workflow":
            if self.process_view.scene():  # There was a previous view which we should restore
                old_transform = self.process_view.transform()

            self.process_model = Workflow(cwl_doc=self.cwl_doc)
            scene = WorkflowScene(self)
            scene.selectionChanged.connect(self.something_selected)
            scene.nodes_added.connect(self.nodes_added)
            scene.double_click.connect(self.something_double_clicked)
            scene.set_workflow(self.process_model)

            if self.process_model.errors:
                logger.warning(self.process_model.errors)
        elif pt in ["CommandLineTool", "ExpressionTool"]:
            self.process_model = Tool(cwl_doc=self.cwl_doc)
            scene = ToolScene(self)
            scene.set_tool(self.process_model)
        else:
            self.process_model = Unk(cwl_doc=self.cwl_doc)
            scene = UnkScene(self)

        self._update_navbar()
        self.process_view.setScene(scene)
        self.process_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if old_transform is not None:
            self.process_view.setTransform(old_transform)
        else:
            self.process_view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)

        t2 = time.time()

        logger.debug("Parsed workflow in {}s ({} bytes) ".format(t1 - t0, len(modified_cwl)))
        logger.debug("Displayed workflow in {}s".format(t2 - t1))

    def _update_navbar(self):
        self.navbar.clear()
        if isinstance(self.process_model, Workflow):
            self.navbar.insertItems(0, sorted(self.process_model.steps.keys()))
            self.navbar.insertSeparator(0)
        self.navbar.insertItems(0, list(self.process_model.section_lines.keys()))

    @Slot()
    def something_selected(self):
        items = self.process_view.scene().selectedItems()
        if len(items) == 1:
            info = items[0].data(0)
            if isinstance(info, str):
                self.highlight(info)
            elif isinstance(info, tuple):
                self.highlight_connection_between_nodes(info)

    def highlight(self, info: str):
        if info in special_ids_for_io:
            self.highlight_workflow_io(info)
        elif info in self.process_model.section_lines:
            self.code_editor.scroll_to(self.process_model.section_lines[info][0].line)
        else:
            self.highlight_step(info)

    def highlight_workflow_io(self, info: str):
        sec = self.process_model.section_lines.get(info)
        if sec is not None:
            self.code_editor.scroll_to(sec[0].line)
            if info == special_id_for_inputs:
                conn = [c for c in self.process_model.connections if c.src.node_id is None]
                color = Qt.green
            else:
                conn = [c for c in self.process_model.connections if c.dst.node_id is None]
                color = Qt.cyan
            self.populate_connection_table(info, [(color, conn)])

    def highlight_step(self, info: str, focus_conn=True):
        if info not in self.process_model.steps:
            return "No step with id: {}".format(info)

        step = self.process_model.steps[info]
        logger.debug("Scroll to line {}".format(step.line[0]))
        self.code_editor.scroll_to(step.line[0])

        inbound_conn = [c for c in self.process_model.connections if c.dst.node_id == info]
        outbound_conn = [c for c in self.process_model.connections if c.src.node_id == info]

        self.populate_connection_table(
            step.id, [(Qt.green, inbound_conn), (Qt.cyan, outbound_conn)], focus_conn=focus_conn)

        return "Selected step with id: {}".format(info)

    def highlight_connection_between_nodes(self, info: tuple):
        def src_is_input(x): return x.src.node_id is None

        def src_is_node(x): return x.src.node_id == id1

        def dst_is_output(x): return x.dst.node_id is None

        def dst_is_node(x): return x.dst.node_id == id2

        id1, id2 = info

        cond1 = src_is_input if id1 == special_id_for_inputs else src_is_node
        cond2 = dst_is_output if id2 == special_id_for_outputs else dst_is_node

        conn = [c for c in self.process_model.connections if cond1(c) and cond2(c)]
        self.populate_connection_table(str(info), [(Qt.white, conn)])

    def populate_connection_table(self, title, conns: [dict], focus_conn=True):
        row, col = 0, 0
        self.conn_table.clear()
        self.conn_table.setColumnCount(1)
        self.conn_table.setRowCount(sum(len(c) for _, c in conns))
        self.conn_table.setHorizontalHeaderLabels([title])
        for color, conn_grp in conns:
            for conn in conn_grp:
                item = QTableWidgetItem(str(conn))
                item.setData(Qt.UserRole, conn)  # All other roles try to replace as display text
                item.setBackgroundColor(color)
                self.conn_table.setItem(row, col, item)
                row += 1

        if focus_conn:
            self.utility_tab_widget.setCurrentIndex(1)  # Make sure we can see the table

    @Slot(int, int)
    def connection_clicked(self, row, col):
        conn = self.conn_table.item(row, col).data(Qt.UserRole)
        logger.debug("Scroll to line {}".format(conn.line[0]))
        self.code_editor.scroll_to(conn.line[0])

    @Slot(QGraphicsSceneMouseEvent)
    def something_double_clicked(self, event):
        items = self.process_view.scene().selectedItems()
        if len(items) == 0:
            self.process_view.reset_zoom()
            # self.process_view.fitInView(self.process_view.scene().sceneRect(), Qt.KeepAspectRatio)
            return

        steps = [self.process_model.steps[item.data(0)] for item in items
                 if item.data(0) not in special_ids_for_io
                 and isinstance(item.data(0), str)]
        # exclude workflow inputs/outputs and connecting lines (which are tuples)
        if steps:
            self.scene_double_clicked.emit(steps)

    @Slot(list)
    def nodes_added(self, cwl_path_list):
        blk = QSignalBlocker(self.code_editor)
        for p in cwl_path_list:
            edit = self.process_model.add_step(p)
            self.code_editor.insert_text(edit)
        self.programmatic_edit()
