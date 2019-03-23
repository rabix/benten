import time

from PySide2.QtWidgets import \
    (QWidget, QComboBox, QLabel, QTabWidget, QTableWidget, QAbstractItemView, QHBoxLayout,
     QVBoxLayout, QSplitter, QShortcut, QGraphicsSceneMouseEvent)
from PySide2.QtCore import Qt, QTimer, Slot, Signal
from PySide2.QtGui import QPainter, QKeySequence, QFontDatabase

from ...configuration import Configuration
from ...editing.rootyamlview import RootYamlView, YamlView, TextView, Edit

from ...models.base import special_ids_for_io
from ...models.createmodel import create_model
from ...models.unk import Unk
from ...models.commandlinetool import CommandLineTool
from ...models.workflow import Workflow

from .editorpane import EditorPane
from .processview import ProcessView
from .commandwidget import CommandWidget
from .wiringtable import WiringTable
from .workflowscene import WorkflowScene

import logging
logger = logging.getLogger(__name__)


class ViewWidget(QWidget):

    open_steps = Signal(object)

    def __init__(self, config: Configuration):
        QWidget.__init__(self)

        self.view: (TextView, YamlView, RootYamlView) = None
        self.process_model: (Unk, CommandLineTool, Workflow) = None
        self.config = config

        self.process_view = ProcessView()

        self.utility_tab_widget = QTabWidget()
        self.wiring_table = WiringTable()
        self.command_window = CommandWidget()
        self.utility_tab_widget.addTab(self.command_window, "CMD")

        self.editor_pane = EditorPane(config=self.config)

        self._setup_panes()

        self.is_active_window = False

    def set_view(self, view: (TextView, YamlView, RootYamlView)):
        self.view = view
        self.view.edit_callback = self.set_text
        self.view.delete_callback = self.close

    def _setup_panes(self):
        left_pane = QSplitter()
        left_pane.setHandleWidth(1)
        left_pane.setOrientation(Qt.Vertical)
        left_pane.addWidget(self.process_view)
        left_pane.addWidget(self.utility_tab_widget)
        left_pane.setStretchFactor(0, 3)
        left_pane.setStretchFactor(1, 1)

        main_pane = QSplitter(self)
        main_pane.setHandleWidth(1)
        main_pane.addWidget(left_pane)
        main_pane.addWidget(self.editor_pane)
        main_pane.setStretchFactor(0, 5)
        main_pane.setStretchFactor(1, 3)

        # If we don't put all this in a layout and set zero margin QT puts us in a tiny box within
        # the window
        layout = QHBoxLayout()
        layout.setMargin(0)
        layout.addWidget(main_pane)
        self.setLayout(layout)

    def set_active_window(self):
        """To be called whenever we switch tabs to this window. """
        self.is_active_window = True
        self.editor_pane.setFocus()
        # When we switch back and forth, we expect to be able to see the editor cursor = focus
        self.update_from_code()

    def set_inactive_window(self):
        """To be called whenever we switch away from this window"""
        # self.manual_edit_throttler.flush()
        self.is_active_window = False

    def set_text(self, raw_text: str):
        self.editor_pane.set_text(raw_text)

    # def get_text(self):
    #     # return self.code_editor.toPlainText()
    #     return self.editor_pane.code_editor.cached_text
    #     # This is kind of our local cache
    #
    # def apply_edit(self, edit: Edit):
    #     # blk = QSignalBlocker(self.code_editor)
    #     return self.code_editor.insert_text(edit)

    def save(self):
        self.view.get_root().save()
        # The attached root will be of type CwlDoc which does have a save function

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
        self.wiring_table.setVisible(True)
        if self.utility_tab_widget.count() == 1:
            self.utility_tab_widget.addTab(self.wiring_table, "Connections")

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
            if self.process_model.code_is_same_as(self.yaml_doc().raw_text):
                # Todo: improve the whole CwlDoc vs YamlView structure so we don't have to do
                # awkward things like this
                logger.debug("{}: Update asked for, but code hasn't changed.".
                             format(self.attached_view.full_readable_path or self.attached_view.file_path))
                return

        t0 = time.time()

        if self.view.yaml is None:
            # Ok, these are fatal errors, leaving us in an un-parsable state. The best we
            # can do is set the dict to the last known state
            logger.error("YAML parsing error! Leaving model in last known good state")

        self.process_model = create_model(self.view)
        if self.process_model.cwl_errors:
            logger.warning(self.process_model.cwl_errors)

        logger.debug("Parsed workflow in {}s ({} bytes) ".
                     format(time.time() - t0, len(self.view.raw_text)))

    def _update_navbar(self):
        nav_items = []
        if isinstance(self.process_model, Workflow):
            nav_items += [sorted(self.process_model.steps.keys())]
        nav_items += [list(self.process_model.section_lines.keys())]
        self.editor_pane.set_navbar(nav_items)

    def _update_yaml_error_banner(self):
        #self.yaml_error_banner.setVisible(self.yaml_error() is not None)
        self.editor_pane.mark_problems(self.process_model.cwl_errors)

    @Slot()
    def something_selected(self):
        items = self.process_view.scene().selectedItems()
        if len(items) == 1:
            info = items[0].data(0)
            if isinstance(info, str):
                self.highlight(info)
            elif isinstance(info, tuple):
                self.highlight_connection_between_nodes(info)

    @Slot(list)
    def nodes_added(self, cwl_path_list):
        # blk = QSignalBlocker(self.code_editor)
        for p in cwl_path_list:
            self.update_process_model_from_code()
            self.code_editor.insert_text(self.process_model.add_step(p))
        self.programmatic_edit()

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
            self.open_steps.emit((self.attached_view, steps))
