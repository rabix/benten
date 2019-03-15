"""A small class handling instructions on what kind of edits to do to a document"""
from typing import List


class EditMark:
    def __init__(self, line=0, column=0):
        self.line, self.column = line, column

    def __repr__(self):  # Helpful for debugging
        return "({}, {})".format(self.line, self.column)


class Edit:
    def __init__(self, start: EditMark, end: EditMark, text: str, text_lines: List[str]):
        self.start, self.end, self.text, self.text_lines = start, end, text, text_lines

    def __repr__(self):  # Helpful for debugging
        return "{}, {}: {}".format(self.start, self.end, self.text[:10])
