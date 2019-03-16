"""Supplies functions to navigate in the document, setd out calls to TabWidget to open up new
tabs and so on. It is responsible for hooking up various widgets to the freshly created navigation
functions. It expects self.process_model to be available"""

from PySide2.QtWidgets import \
    (QWidget, QComboBox, QLabel, QTabWidget, QTableWidget, QTableWidgetItem, QAbstractItemView,
     QHBoxLayout, QVBoxLayout, QSplitter, QShortcut, QGraphicsSceneMouseEvent)
from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot, Signal

from ...models.workflow import (Workflow, Step,
                                special_id_for_inputs, special_id_for_outputs, special_ids_for_io)

import logging
logger = logging.getLogger(__name__)


class ViewWidgetNavigation:

    open_steps = Signal(object)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
            self.open_steps.emit((self.parent_view, steps))

    def step_ids_to_open(self, step_ids):
        steps = [step for step in self.process_model.steps.values() if step.id in step_ids ]
        self.open_steps.emit((self.parent_view, steps))

    @Slot(list)
    def nodes_added(self, cwl_path_list):
        blk = QSignalBlocker(self.code_editor)
        for p in cwl_path_list:
            self.update_process_model_from_code()
            self.code_editor.insert_text(self.process_model.add_step(p))
        self.programmatic_edit()
