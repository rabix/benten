"""Basic editing operations"""
import PySide2.QtGui as QtGui

from ....editing.edit import Edit  # God, we're in deep


class BentenBasic:

    def scroll_to(self, zero_indexed_line_no):
        return self.gotoBlock(zero_indexed_line_no)

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

    def insert_text(self, edit: Edit):

        doc = self.document()

        cursor = QtGui.QTextCursor(doc)
        cursor.clearSelection()

        cursor.beginEditBlock()

        if edit.start.line == doc.blockCount():
            if edit.start.column != 0:
                raise RuntimeError("Implementation error! File bug report with stack trace please")
            cursor.movePosition(cursor.End)
            cursor.insertText("\n")
        else:
            cursor.movePosition(cursor.Start)
            cursor.movePosition(cursor.NextBlock, n=edit.start.line)  # blocks == lines
            cursor.movePosition(cursor.Right, n=edit.start.column)

        if edit.end is not None:
            delta_line = edit.end.line - edit.start.line
            delta_col = edit.end.column - edit.start.column
            if delta_line > 0:
                cursor.movePosition(cursor.NextBlock, cursor.KeepAnchor, n=delta_line)
            else:
                cursor.movePosition(cursor.Right, cursor.KeepAnchor, n=delta_col)

        cursor.insertText(edit.text)

        cursor.endEditBlock()

        self.updateMargins()
        self.setTextCursor(cursor)

