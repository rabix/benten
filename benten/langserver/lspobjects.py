"""Collection of common LSP objects"""
from typing import List
from enum import IntEnum


def to_dict(v):
    if isinstance(v, LSPObject):
        return {
            k: to_dict(_v)
            for k, _v in v.__dict__.items() if _v is not None
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

    def __hash__(self):
        return hash((self.line, self.character))

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.line == other.line and self.character == other.character


class Range(LSPObject):
    def __init__(self, start: Position, end: Position):
        self.start = start
        self.end = end

    def __hash__(self):
        return hash((self.start, self.end))

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.start == other.start and self.end == other.end


class TextEdit(LSPObject):
    def __init__(self, _range: Range, new_text: str):
        self.range = _range
        self.newText = new_text


class Location(LSPObject):
    def __init__(self, uri, _range: Range=Range(Position(0, 0), Position(0, 0))):
        self.uri = uri
        self.range = _range


class DiagnosticSeverity(IntEnum):
    Error = 1
    Warning = 2
    Information = 3
    Hint = 4


class Diagnostic(LSPObject):
    def __init__(self,
                 _range: Range, message: str,
                 severity: DiagnosticSeverity=None,
                 code: str=None,
                 source: str=None):
        self.range = _range
        self.message = message
        self.severity = severity
        self.code = code
        self.source = source

    def __hash__(self):
        return hash((self.range, self.message))

    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.range == other.range and self.message == other.message


def mark_problem(message, severity, value=None):
    if value is None:
        start = Position(0, 0)
        end = Position(0, 1)
    else:
        start = Position(value.start.line, value.start.column)
        end = Position(value.end.line, value.end.column)

    return Diagnostic(
        _range=Range(start=start, end=end),
        message=message,
        severity=severity,
        code="CWL err",
        source="Benten")


class PublishDiagnosticsParams(LSPObject):
    def __init__(self, uri, diagnostics: List[Diagnostic]):
        self.uri = uri
        self.diagnostics = diagnostics


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
                 text_edit: TextEdit = None, additional_text_edits: [TextEdit] = None,
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
        self.insertTextFormat = insert_text_format
        self.textEdit = text_edit
        self.additionalTextEdits = additional_text_edits

    def set_range(self, _range: Range):
        self.textEdit.range = _range

    @classmethod
    def from_snippet(
            cls,
            snippet: dict):

        if "label" not in snippet:
            snippet["label"] = "Unknown"

        try:
            snippet["kind"] = CompletionItemKind[snippet["kind"]]
        except KeyError:
            snippet["kind"] = CompletionItemKind.Text

        snippet["insert_text_format"] = InsertTextFormat.Snippet
        # snippet["insert_text"] = snippet.get("snippet")
        snippet["text_edit"] = TextEdit(
            _range=Range(
                start=Position(line=0, character=0),
                end=Position(line=0, character=0)
            ),
            new_text=snippet.get("text_edit"))

        return cls(**snippet)


class CompletionList(LSPObject):
    def __init__(self, is_incomplete: bool = False, items: [CompletionItem] = None):
        self.isIncomplete = is_incomplete
        self.items = items or []


class SymbolKind(IntEnum):
    File = 1
    Module = 2
    Namespace = 3
    Package = 4
    Class = 5
    Method = 6
    Property = 7
    Field = 8
    Constructor = 9
    Enum = 10
    Interface = 11
    Function = 12
    Variable = 13
    Constant = 14
    String = 15
    Number = 16
    Boolean = 17
    Array = 18
    Object = 19
    Key = 20
    Null = 21
    EnumMember = 22
    Struct = 23
    Event = 24
    Operator = 25
    TypeParameter = 26


class DocumentSymbol(LSPObject):
    def __init__(self, name, kind, _range, selection_range, detail=None, children=None):
        self.name = name
        self.detail = detail
        self.kind: SymbolKind = kind
        self.range: Range = _range
        self.selectionRange: Range = selection_range
        self.children: List[DocumentSymbol] = children
