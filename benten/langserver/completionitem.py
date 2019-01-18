from enum import IntEnum


from benten.langserver.lspobjects import LSPObject, TextEdit


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
                 insert_text: str=None,
                 text_edit: TextEdit=None, additional_text_edits: [TextEdit]=[],
                 kind: CompletionItemKind=CompletionItemKind.Text,
                 insert_text_format: InsertTextFormat=None,
                 detail: str=None, documentation: str=None, preselect: bool=None,
                 sort_text: str=None, filter_text:str=None):
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


class CompletionList(LSPObject):
    def __init__(self, is_incomplete: bool=True, items: [CompletionItem]=[]):
        self.isIncomplete = is_incomplete
        self.items = items
