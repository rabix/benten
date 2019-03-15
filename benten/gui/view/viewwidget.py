from PySide2.QtWidgets import QWidget
from PySide2.QtCore import QSignalBlocker

from ...editing.yamlview import EditorInterface, Edit

from .viewwidgetbase import ViewWidgetBase
from .viewwidgetnavigation import ViewWidgetNavigation
from .viewwidgetcommands import ViewWidgetCommands
from .viewwidgetmodels import ViewWidgetModels


class ViewWidget(EditorInterface, ViewWidgetCommands, ViewWidgetModels, ViewWidgetNavigation, ViewWidgetBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def set_text(self, raw_text: str):
        blk = QSignalBlocker(self.code_editor)
        self.code_editor.set_text(raw_text)

    def get_text(self):
        return self.code_editor.toPlainText()

    def apply_edit(self, edit: Edit):
        blk = QSignalBlocker(self.code_editor)
        return self.code_editor.insert_text(edit)
