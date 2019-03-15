"""This contains the setup of all the widget components, just to keep things neat"""
from PySide2.QtWidgets import \
    (QWidget, QComboBox, QLabel, QTabWidget, QTableWidget, QTableWidgetItem, QAbstractItemView,
     QHBoxLayout, QVBoxLayout, QSplitter, QShortcut, QGraphicsSceneMouseEvent)
from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot, Signal
from PySide2.QtGui import QTextCursor, QPainter, QFont, QKeySequence

from ...models.unk import Unk
from ...models.commandlinetool import CommandLineTool
from ...models.workflow import Workflow, special_id_for_inputs, special_id_for_outputs, special_ids_for_io

from ..codeeditor.editor import CodeEditor
from .processview import ProcessView
from .commandwidget import CommandWidget
from .workflowscene import WorkflowScene


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


class ViewWidgetBase(QWidget):

    def __init__(self):
        QWidget.__init__(self)

        self.code_editor: CodeEditor = self._setup_code_editor()
        self.navbar = self._setup_navbar()
        self.yaml_error_banner = self._setup_yaml_banner()
        self.process_view: ProcessView = ProcessView(None)
        self.utility_tab_widget, self.command_window, self.conn_table \
            = self._setup_utility_tab()
        self._setup_panes()
        self.shortcuts = self._setup_shortcuts()

        self.manual_edit_throttler = ManualEditThrottler()
        self.manual_edit_throttler.timer.timeout.connect(self.manual_edit)

        self.process_model: (Unk, CommandLineTool, Workflow) = None

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

    @staticmethod
    def _setup_yaml_banner():
        banner = QLabel("Document has YAML errors")
        banner.setStyleSheet("QLabel { background-color : red; color : white; }")
        banner.setVisible(False)
        return banner

    def _setup_utility_tab(self):
        utility_tab_widget = QTabWidget()

        command_window = CommandWidget(self)

        conn_table = QTableWidget()
        conn_table.horizontalHeader().setStretchLastSection(True)
        conn_table.verticalHeader().setVisible(False)
        conn_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        conn_table.cellClicked.connect(self.connection_clicked)

        utility_tab_widget.addTab(command_window, "CMD")

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
        right_pane.addWidget(self.yaml_error_banner)
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

    def _setup_shortcuts(self):

        @Slot()
        def toggle_cmd_focus():
            if self.code_editor.hasFocus():
                self.command_window.command_line.setFocus()
            else:
                self.code_editor.setFocus()

        command_window_shortcut = QShortcut(QKeySequence("Ctrl+P"), self)
        command_window_shortcut.activated.connect(toggle_cmd_focus)

        return [command_window_shortcut]

    def set_active_window(self):
        """To be called whenever we switch tabs to this window. """
        self.is_active_window = True
        self.code_editor.setFocus()
        # When we switch back and forth, we expect to be able to see the editor cursor = focus

    def set_inactive_window(self):
        """To be called whenever we switch away from this window"""
        self.manual_edit_throttler.flush()
        self.is_active_window = False

    def update_from_code(self):
        pass

    @Slot()
    def user_still_typing(self):
        """Called whenever the editor contents are changed. We restrict this to actual typing."""
        logger.debug("User typing ...")
        self.manual_edit_throttler.restart_edit_clock()

    @Slot()
    def manual_edit(self):
        """Called when the user is done with their burst of typing, or we switch away from this tab"""
        logger.debug("Registering manual edit ...")
        self._register_edit()

    @Slot()
    def programmatic_edit(self):
        """Called when we have executed a programmatic edit"""
        logger.debug("Registering programmatic edit ...")
        self._register_edit()

    def _register_edit(self):
        pass

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
            return

        steps = [self.process_model.steps[item.data(0)] for item in items
                 if item.data(0) not in special_ids_for_io
                 and isinstance(item.data(0), str)]
        # exclude workflow inputs/outputs and connecting lines (which are tuples)
        if steps:
            self.steps_to_open.emit(steps)

    def step_ids_to_open(self, step_ids):
        steps = [step for step in self.process_model.steps.values() if step.id in step_ids ]
        self.steps_to_open.emit(steps)

    @Slot(list)
    def nodes_added(self, cwl_path_list):
        blk = QSignalBlocker(self.code_editor)
        for p in cwl_path_list:
            self.update_process_model_from_code()
            self.code_editor.insert_text(self.process_model.add_step(p))
        self.programmatic_edit()
