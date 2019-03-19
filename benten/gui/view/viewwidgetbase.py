"""This contains the setup of all the widget components, just to keep things neat"""
from PySide2.QtWidgets import \
    (QWidget, QComboBox, QLabel, QTabWidget, QTableWidget, QAbstractItemView, QHBoxLayout,
     QVBoxLayout, QSplitter, QShortcut)
from PySide2.QtCore import Qt, QTimer, Slot, Signal
from PySide2.QtGui import QKeySequence, QFontDatabase

from ...configuration import Configuration

from ...models.unk import Unk
from ...models.commandlinetool import CommandLineTool
from ...models.workflow import Workflow

#from ..codeeditor.editor import CodeEditor
from ..ace.editor import Editor
from .processview import ProcessView
from .commandwidget import CommandWidget


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

    def __init__(self, config: Configuration):
        QWidget.__init__(self)

        self.config = config

        self.code_editor: Editor = self._setup_code_editor()
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
        ce = Editor(config=self.config)
        # ce.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
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
