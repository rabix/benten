class OutOfHistory(Exception):
    pass


class History:
    """The history stores the CWL as a raw text. When we retrieve something from the history
    we re-parse it into a workflow. Raw text is cheaper to store than CommentedMap and allows
    clean interop with manual edits."""
    def __init__(self, cwl_txt: str):
        self.history = [cwl_txt]
        self.index = 0

    def append(self, cwl_txt: str):
        self.history = self.history[:self.index + 1]
        self.history += [cwl_txt]
        self.index = len(self.history) - 1

    def current(self):
        return self.history[self.index]

    def undo(self) -> str:
        if self.index > 0:
            self.index -= 1
            return self.history[self.index]
        else:
            raise OutOfHistory

    def redo(self) -> str:
        if self.index < len(self.history) - 1:
            self.index += 1
            return self.history[self.index]
        else:
            raise OutOfHistory



