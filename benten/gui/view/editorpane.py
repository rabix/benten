from typing import List

from PySide2.QtWidgets import \
    (QWidget, QComboBox, QLabel, QTabWidget, QTableWidget, QAbstractItemView, QHBoxLayout,
     QVBoxLayout, QSplitter, QShortcut)
from PySide2.QtCore import Qt, QTimer, Slot, Signal
from PySide2.QtGui import QKeySequence, QFontDatabase

from ...editing.documentproblem import DocumentProblem
from ...models.workflow import Workflow
from ..ace.editor import Editor


class EditorPane(QWidget):

    step_selected = Signal(str)
    text_available = Signal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.config = config

        self.code_editor: Editor = self._setup_code_editor()
        self.navbar = self._setup_navbar()
        self.yaml_error_banner = self._setup_yaml_banner()

        pane = QVBoxLayout()
        pane.addWidget(self.navbar)
        pane.addWidget(self.code_editor)
        pane.addWidget(self.yaml_error_banner)
        pane.setMargin(0)
        pane.setSpacing(0)
        self.setLayout(pane)

    @Slot(str)
    def set_text(self, text):
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
        # Todo: if there is an yaml error, raise the banner and link it to scrolling to
        # the error on click otherwise clear the banner

    def _setup_code_editor(self):
        ce = Editor(config=self.config)
        ce.new_text_available.connect(self.text_available.emit)
        return ce

    def _setup_navbar(self):
        navbar = QComboBox()
        navbar.activated[str].connect(lambda x: self.step_selected.emit(x))
        return navbar

    @staticmethod
    def _setup_yaml_banner():
        banner = QLabel("Document has YAML errors")
        banner.setStyleSheet("QLabel { background-color : red; color : white; }")
        banner.setVisible(False)
        return banner

    def update_navbar(self):
        self.navbar.clear()
        if isinstance(self.process_model, Workflow):
            self.navbar.insertItems(0, sorted(self.process_model.steps.keys()))
            self.navbar.insertSeparator(0)
        self.navbar.insertItems(0, list(self.process_model.section_lines.keys()))
