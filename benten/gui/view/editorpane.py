from typing import List

from PySide2.QtWidgets import \
    (QWidget, QComboBox, QLabel, QPushButton, QTabWidget, QTableWidget, QAbstractItemView, QHBoxLayout,
     QVBoxLayout, QSplitter, QShortcut)
from PySide2.QtCore import Qt, QTimer, Slot, Signal
from PySide2.QtGui import QKeySequence, QFontDatabase

from ...editing.documentproblem import DocumentProblem
from ...models.workflow import Workflow
from ..ace.editor import Editor
from .commandwidget import CommandWidget

import logging
logger = logging.getLogger(__name__)


class ProblemHandler(QPushButton):
    # A souped up button to handle our error navigation

    goto = Signal(int, str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setFlat(True) -> this screws with the colors on mac ...
        self.setMaximumHeight(30)
        self.setVisible(False)

        self.show_next_problem = QShortcut(QKeySequence("Ctrl+N"), self)
        self.show_next_problem.activated.connect(self.next_problem_line)

        self.clicked.connect(self.next_problem_line)

        self.problems = []
        self.next_problem = 0

    def set_problems(self, problems: List[DocumentProblem]):
        self.problems = sorted(problems, key=lambda x: x.line)
        self.next_problem = 0
        if DocumentProblem.Class.cwl in [p.problem_class for p in problems]:
            self.setText("Document has CWL issues")
            self.setStyleSheet("QPushButton { background-color : orange; color : white; }")
            self.setVisible(True)
        elif DocumentProblem.Class.yaml in [p.problem_class for p in problems]:
            self.setText("Document has YAML issues")
            self.setStyleSheet("QPushButton { background-color : red; color : white; }")
            self.setVisible(True)
        else:
            self.setVisible(False)

    @Slot()
    def next_problem_line(self):
        if self.problems:
            self.goto.emit(self.problems[self.next_problem].line, None)
            self.next_problem += 1
            if self.next_problem == len(self.problems):
                self.next_problem = 0


class EditorPane(QWidget):

    step_selected = Signal(str)
    text_available = Signal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config

        self.code_editor: Editor = self._setup_code_editor()
        self.navbar = self._setup_navbar()
        self.problem_handler = ProblemHandler()
        self.problem_handler.goto.connect(self.goto)
        self.command_widget = CommandWidget(editor=self.code_editor)
        self.command_widget.setVisible(False)

        self.cmd_toggle = QShortcut(QKeySequence("Ctrl+P"), self)
        self.cmd_toggle.activated.connect(self.toggle_command_widget)

        ed_layout = QVBoxLayout()
        ed_layout.addWidget(self.navbar)
        ed_layout.addWidget(self.code_editor)
        ed_layout.addWidget(self.problem_handler)
        ed_layout.setMargin(0)
        ed_layout.setSpacing(0)
        ed_widget = QWidget()
        ed_widget.setLayout(ed_layout)

        main_pane = QSplitter(self)
        main_pane.setHandleWidth(1)
        main_pane.setOrientation(Qt.Vertical)
        main_pane.addWidget(ed_widget)
        main_pane.addWidget(self.command_widget)
        main_pane.setStretchFactor(0, 5)
        main_pane.setStretchFactor(1, 3)

        # If we don't put all this in a layout and set zero margin QT puts us in a tiny box within
        # the window
        main_layout = QHBoxLayout()
        main_layout.setMargin(0)
        main_layout.addWidget(main_pane)
        self.setLayout(main_layout)

    @Slot()
    def toggle_command_widget(self):
        self.command_widget.setVisible(not self.command_widget.isVisible())

    @Slot(str)
    def set_text(self, text):
        logger.debug("Sending text to editor")
        self.code_editor.set_text(text)

    @Slot()
    def flush(self):
        # todo: implement this if we have glitches when switching tabs fast
        pass

    @Slot(object)
    def set_navbar(self, items_l: List[List[str]]):
        self.navbar.clear()
        for n, items in enumerate(items_l):
            if n > 0: self.navbar.insertSeparator(0)
            self.navbar.insertItems(0, items)

    @Slot(int, str)
    def goto(self, line, step_id):
        self.code_editor.scroll_to(line)
        if step_id:
            self.navbar.setCurrentText(step_id)

    @Slot(object)
    def mark_problems(self, problems: List[DocumentProblem]):
        self.code_editor.mark_errors(problems)
        self.problem_handler.set_problems(problems)

    def _setup_code_editor(self):
        ce = Editor(config=self.config)
        ce.new_text_available.connect(self.text_available.emit)
        return ce

    def _setup_navbar(self):
        navbar = QComboBox()
        navbar.activated[str].connect(lambda x: self.step_selected.emit(x))
        return navbar

    def update_navbar(self):
        self.navbar.clear()
        if isinstance(self.process_model, Workflow):
            self.navbar.insertItems(0, sorted(self.process_model.steps.keys()))
            self.navbar.insertSeparator(0)
        self.navbar.insertItems(0, list(self.process_model.section_lines.keys()))
