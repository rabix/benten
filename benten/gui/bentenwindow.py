"""Provides a view into a CWL component, like a workflow. The view can be of a whole CWL file
or a part of a CWL file, like an in-lined step."""
import pathlib
import time

from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot, Signal
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QSplitter, QTableWidget, QTableWidgetItem, QWidget, \
    QAbstractItemView, QGraphicsSceneMouseEvent, QTabWidget, QComboBox, QLabel, QShortcut
from PySide2.QtGui import QTextCursor, QPainter, QFont, QKeySequence

from ..implementationerror import ImplementationError
from ..editing.edit import Edit, EditMark
from ..editing.yamlview import YamlView, EditorInterface, Contents

from ..models.createmodel import create_model
from ..models.unk import Unk
from ..models.tool import Tool
from ..models.commandlinetool import CommandLineTool
from ..models.workflow import Workflow, special_id_for_inputs, special_id_for_outputs, special_ids_for_io

from .codeeditor.editor import CodeEditor
from .processview import ProcessView
from .command.commandwidget import CommandWidget
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


class BentenWindow(EditorInterface, QWidget):

    steps_to_open = Signal(object)
    edit_registered = Signal(object)

    def __init__(self, view: YamlView, benten_main_window):
        QWidget.__init__(self)

        self.attached_view = view
        self.bmw = benten_main_window

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

        self.cwl_doc = cwl_doc
        self.code_editor.set_text(self.cwl_doc.raw_cwl)

        self.step_id = None
        self.process_model: (Unk, Tool, Workflow) = None

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

    def set_text(self, raw_text: str):
        blk = QSignalBlocker(self.code_editor)
        self.code_editor.set_text(raw_text)

    def get_text(self):
        return self.code_editor.toPlainText()

    def apply_edit(self, edit: Edit):
        return self.code_editor.insert_text(edit)

    # def set_document(self, cwl_doc):
    #     # This registers as a manual edit but we wish to skip the throttler
    #     blk = QSignalBlocker(self.code_editor)
    #     self.cwl_doc = cwl_doc
    #     self.code_editor.set_text(self.cwl_doc.raw_text)

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
        self._register_edit()

    @Slot()
    def programmatic_edit(self):
        """Called when we have executed a programmatic edit"""
        logger.debug("Registering programmatic edit ...")
        self._register_edit()

    def _register_edit(self):
        op_flag = self.attached_view.fetch_from_editor()
        self.update_from_code()

    # This only happens when we are in focus and the code has changed
    # It is only here that we do the (semi)expensive parsing computation
    @Slot()
    def update_from_code(self):

        if not self.is_active_window:
            # Defer updating until we can be seen
            return

        self.update_process_model_from_code()

        t1 = time.time()

        if isinstance(self.process_model, Workflow):
            self.configure_as_workflow()
        elif isinstance(self.process_model, CommandLineTool):
            self.configure_as_tool()
        else:
            self.configure_as_unknown()

        self._update_navbar()
        self._update_yaml_error_banner()

        t2 = time.time()
        logger.debug("Displayed workflow in {}s".format(t2 - t1))

    def configure_as_workflow(self):
        old_transform = None
        if self.process_view.scene():  # There was a previous view which we should restore
            old_transform = self.process_view.transform()
        scene = WorkflowScene(self)
        scene.selectionChanged.connect(self.something_selected)
        scene.nodes_added.connect(self.nodes_added)
        scene.double_click.connect(self.something_double_clicked)
        scene.set_workflow(self.process_model)

        self.process_view.setScene(scene)
        self.process_view.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        if old_transform is not None:
            self.process_view.setTransform(old_transform)
        else:
            self.process_view.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)
        self.process_view.setVisible(True)
        self.conn_table.setVisible(True)
        if self.utility_tab_widget.count() == 1:
            self.utility_tab_widget.addTab(self.conn_table, "Connections")

    def configure_as_tool(self):
        self.process_view.setVisible(False)
        if self.utility_tab_widget.count() == 2:
            self.utility_tab_widget.removeTab(1)

    def configure_as_unknown(self):
        self.process_view.setVisible(False)
        if self.utility_tab_widget.count() == 2:
            self.utility_tab_widget.removeTab(1)

    # We refactored this out of update_from_code() because some chain edits
    # need us to recompute the process model (for proper formatting of subsequent edits)
    # but we don't want to waste time drawing each time - we can do that at the end
    def update_process_model_from_code(self):
        if self.process_model is not None:
            if self.process_model.code_is_same_as(self.attached_view.doc.raw_text):
                logger.debug("{}: Update asked for, but code hasn't changed.".format(self.step_id))
                return

        t0 = time.time()

        parse_result = self.attached_view.doc.parse_yaml()
        if parse_result & Contents.ParseFail:
            # Ok, these are fatal errors, leaving us in an un-parsable state. The best we
            # can do is set the dict to the last known state
            logger.error("YAML parsing error! Leaving model in last known good state")

        self.process_model = create_model(self.attached_view.doc)
        if self.process_model.cwl_errors:
            logger.warning(self.process_model.cwl_errors)

        logger.debug("Parsed workflow in {}s ({} bytes) ".
                     format(time.time() - t0, len(self.attached_view.doc.raw_text)))

    def _update_navbar(self):
        self.navbar.clear()
        if isinstance(self.process_model, Workflow):
            self.navbar.insertItems(0, sorted(self.process_model.steps.keys()))
            self.navbar.insertSeparator(0)
        self.navbar.insertItems(0, list(self.process_model.section_lines.keys()))

    def _update_yaml_error_banner(self):
        self.yaml_error_banner.setVisible(self.cwl_doc.is_invalid())

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

    def create_scaffold(self, args):
        blk = QSignalBlocker(self.code_editor)

        if self.cwl_doc.raw_cwl:
            return "Document not empty, will not create scaffold"

        arg = args[0] if isinstance(args, list) else args

        choices = {
            "clt": "command-line-tool.cwl",
            "et": "expression-tool.cwl",
            "wf": "workflow.cwl"
        }
        scaffold_path = pathlib.Path(self.bmw.config.getpath("cwl", "template_dir"),
                                     choices.get(arg, "doesnotexist"))

        if scaffold_path.exists():
            edit = Edit(start=EditMark(line=0, column=0), end=None,
                        text=scaffold_path.open("r").read())
            self.code_editor.insert_text(edit)
            self.programmatic_edit()
            return "Added scaffold from file {}".format(scaffold_path)
        else:
            return "No scaffold for process type {}. Valid arguments are {}".format(arg, list(choices.keys()))

    def scaffold_new_step(self, args):
        blk = QSignalBlocker(self.code_editor)

        if self.cwl_doc.type() != "Workflow":
            return "Can only add new step to workflow"

        if not 0 < len(args) < 3:
            return "Arguments are <step_id> [path]"

        step_id = args[0]
        path = pathlib.Path(args[1]) if len(args) > 1 else None
        self.code_editor.insert_text(self.process_model.add_step(path, step_id))
        self.programmatic_edit()
        return "Added new step"

    def scaffold_docker(self, args):
        blk = QSignalBlocker(self.code_editor)

        if self.cwl_doc.type() != "CommandLineTool":
            return "Can only add DockerRequirement to CommandLineTool"

        if len(args) != 1:
            return "Arguments are <docker_image>"

        self.code_editor.insert_text(self.process_model.add_docker(args[0]))
        self.programmatic_edit()
        return "Added DockerRequirement"
