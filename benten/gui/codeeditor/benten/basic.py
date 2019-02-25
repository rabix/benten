"""Basic editing operations"""
import PySide2.QtGui as QtGui

from ....editing.edit import Edit  # God, we're in deep


class BentenBasic:

    def set_text(self, text):
        # This attempts to preserve the editor state before and after the insert
        # from https://www.qtcentre.org/threads/13933-Restoring-cursor-position-in-QTextEdit

        scroll_value = self.verticalScrollBar().value()
        original_cursor_pos = self.textCursor().position()

        # https://programtalk.com/python-examples/PySide2.QtGui.QTextCursor/
        # https://www.qtcentre.org/threads/43268-Setting-Text-in-QPlainTextEdit-without-Clearing-Undo-Redo-History
        doc = self.document()
        insert_cursor = QtGui.QTextCursor(doc)
        insert_cursor.select(QtGui.QTextCursor.SelectionType.Document)
        insert_cursor.insertText(text)
        self.updateMargins()

        self.verticalScrollBar().setValue(scroll_value)
        new_cursor = self.textCursor()
        new_cursor.setPosition(original_cursor_pos, QtGui.QTextCursor.MoveAnchor)
        self.setTextCursor(new_cursor)
