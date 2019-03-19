"""This mixin class is responsible for creating models from the YamlView/YamlDoc"""
import time

from PySide2.QtGui import QPainter
from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot, Signal

from ...editing.yamldoc import Contents

from ...models.createmodel import create_model
from ...models.unk import Unk
from ...models.commandlinetool import CommandLineTool
from ...models.workflow import Workflow

from .workflowscene import WorkflowScene

import logging
logger = logging.getLogger(__name__)


class ViewWidgetModels:

    def set_active_window(self):
        """To be called whenever we switch tabs to this window. """
        super().set_active_window()
        self.update_from_code()

    def _register_edit(self):
        op_flag = self.push_changes()
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
            if self.process_model.code_is_same_as(self.yaml_doc().raw_text):
                # Todo: improve the whole CwlDoc vs YamlView structure so we don't have to do
                # awkward things like this
                logger.debug("{}: Update asked for, but code hasn't changed.".
                             format(self.attached_view.full_readable_path or self.attached_view.file_path))
                return

        t0 = time.time()

        parse_result = self.parse_yaml()
        if parse_result & Contents.ParseFail:
            # Ok, these are fatal errors, leaving us in an un-parsable state. The best we
            # can do is set the dict to the last known state
            logger.error("YAML parsing error! Leaving model in last known good state")

        self.process_model = create_model(self.yaml_doc())
        if self.process_model.cwl_errors:
            logger.warning(self.process_model.cwl_errors)

        logger.debug("Parsed workflow in {}s ({} bytes) ".
                     format(time.time() - t0, len(self.yaml_doc().raw_text)))

    def _update_navbar(self):
        self.navbar.clear()
        if isinstance(self.process_model, Workflow):
            self.navbar.insertItems(0, sorted(self.process_model.steps.keys()))
            self.navbar.insertSeparator(0)
        self.navbar.insertItems(0, list(self.process_model.section_lines.keys()))

    def _update_yaml_error_banner(self):
        self.yaml_error_banner.setVisible(self.yaml_error() is not None)
