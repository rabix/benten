"""Collection of common LSP objects"""
from enum import IntEnum


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


class CodeActionKind:
    QuickFix = 'quickfix'
    CodeActionKind = 'refactor'
    RefactorExtract = 'refactor.extract'
    RefactorInline = 'refactor.inline'
    RefactorRewrite = 'refactor.rewrite'
    Source = 'source'
    SourceOrganizeImports = 'source.organizeImports'


class CompletionItemKind(IntEnum):
    Text = 1
    Method = 2
    Function = 3
    Constructor = 4
    Field = 5
    Variable = 6
    Class = 7
    Interface = 8
    Module = 9
    Property = 10
    Unit = 11
    Value = 12
    Enum = 13
    Keyword = 14
    Snippet = 15
    Color = 16
    File = 17
    Reference = 18
    Folder = 19
    EnumMember = 20
    Constant = 21
    Struct = 22
    Event = 23
    Operator = 24
    TypeParameter = 25


class InsertTextFormat(IntEnum):
    PlainText = 1
    Snippet = 2


class CompletionItem(LSPObject):
    def __init__(self,
                 label: str,
                 insert_text: str = None,
                 text_edit: TextEdit = None, additional_text_edits: [TextEdit] = [],
                 kind: CompletionItemKind = CompletionItemKind.Text,
                 insert_text_format: InsertTextFormat = None,
                 detail: str = None, documentation: str = None, preselect: bool = None,
                 sort_text: str = None, filter_text: str = None):
        self.label = label
        self.kind = kind
        self.detail = detail
        self.documentation = documentation
        self.preselect = preselect
        self.sortText = sort_text
        self.filterText = filter_text
        self.insertText = insert_text
        self.insertTextFormat = insert_text_format
        self.textEdit = text_edit
        self.additionalTextEdits = additional_text_edits

    @classmethod
    def from_snippet(cls, snippet: dict):
        ci = CompletionItem(label=label)
        cwl = tpl["cwl"]
        cwl_lines = cwl.split("\n")
        ci.textEdit = TextEdit(line=0, character=0, new_text=cwl_lines[0])
        ci.additionalTextEdits = [
            TextEdit(line=n, character=0, new_text=cwl_lines[n])
            for n in range(1, len(cwl_lines))
        ]
        ci.documentation = tpl["doc"]


class CompletionList(LSPObject):
    def __init__(self, is_incomplete: bool = True, items: [CompletionItem] = None):
        self.isIncomplete = is_incomplete
        self.items = items or []
