"""A small class handling instructions on what kind of edits to do to a document"""


class EditMark:
    def __init__(self, line, column):
        self.line, self.column = line, column

    def __repr__(self):  # Helpful for debugging
        return "({}, {})".format(self.line, self.column)


class Edit:
    def __init__(self, start, end, text):
        self.start, self.end, self.text = start, end, text

    def __repr__(self):  # Helpful for debugging
        return "{} - {}: {}".format(self.start, self.end, self.text[:10])
