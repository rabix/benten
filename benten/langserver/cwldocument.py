"""Holds a given CWL document (there can be several in a session) and implements
a variety of operations the language server can offer"""
import benten
import benten.langserver.configuration as cfg
from benten.langserver.lspobjects import Range, Position
from benten.langserver.completionitem import CompletionItem, CompletionList, TextEdit


# Have to confirm there is no other way to
def convert_template_to_completion_item(label, tpl):
    ci = CompletionItem(label=label)
    cwl = tpl["cwl"]
    cwl_lines = cwl.split("\n")
    ci.textEdit = TextEdit(line=0, character=0, new_text=cwl_lines[0])
    ci.additionalTextEdits = [
        TextEdit(line=n, character=0, new_text=cwl_lines[n])
        for n in range(1, len(cwl_lines))
    ]
    ci.documentation = tpl["doc"]
    return ci


class CwlDocument:

    def __init__(self, base_path, raw_cwl, version, configuration: cfg.Configuration):
        self.base_path = base_path
        self.raw_cwl = raw_cwl
        self.version = version
        self.configuration = configuration

    def did_change(self, changed_text, version):
        self.raw_cwl = changed_text
        self.version = version

    def auto_complete(self, character, line):
        # Just for testing
        return self.autocomplete_on_empty_document()

    def autocomplete_on_empty_document(self):
        items = [
            convert_template_to_completion_item(label, data)
            for label, data in self.configuration.cwl_templates.items()
        ]
        return CompletionList(is_incomplete=False, items=items).to_dict()
