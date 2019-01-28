from PySide2.QtWidgets import QPlainTextEdit


class CodeEditor(QPlainTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
