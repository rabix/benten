"""This is to take care of documents that start with comments etc. so we can offer
to auto complete as a CWL object"""
from .base import Base
from ..langserver.lspobjects import CompletionItem, CompletionList, Position, Range


class PlainText(Base):

    def completions(self, position: Position, snippets: dict):
        return super()._quick_completions(
            position=position, snippets=snippets,
            snippet_keys=["CommandLineTool", "ExpressionTool", "Workflow",
                          "CommandLineTool with script"])
