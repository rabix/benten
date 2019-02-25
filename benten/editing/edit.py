"""A small class handling instructions on what kind of edits to do to a document"""


class EditMark:
    def __init__(self, line, column):
        self.line, self.column = line, column


class Edit:
    def __init__(self, start, end, text):
        self.start, self.end, self.text = start, end, text
