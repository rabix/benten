"""Collection of LSP objects"""


def to_dict(v):
    if isinstance(v, LSPObject):
        return {
            k: to_dict(_v)
            for k, _v in v.__dict__.items() if v is not None
        }
    elif isinstance(v, dict):
        return {
            k: to_dict(_v)
            for k, _v in v.items()
        }
    elif isinstance(v, list):
        return [
            to_dict(_v) for _v in v
        ]
    else:
        return v


class LSPObject:
    def to_dict(self):
        return to_dict(self)


class Position(LSPObject):
    def __init__(self, line, character):
        self.line = line
        self.character = character


class Range(LSPObject):
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end


class TextEdit(LSPObject):
    def __init__(self, line: int, character: int, new_text: str):
        self.range = Range(
            start=Position(line=line, character=character),
            end=Position(line=line, character=character + len(new_text)))
        self.newText = new_text
