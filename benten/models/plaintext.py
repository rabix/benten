"""This is to take care of documents that start with comments etc. so we can offer
to auto complete as a CWL object"""
from .base import Base
from ..langserver.lspobjects import CompletionItem, CompletionList, Position


class PlainText(Base):

    def completions(self, position: Position, snippets: dict):
        return CompletionList(
            is_incomplete=False,
            items=[
                snip for k, snip in snippets.items()
                if k in ["CommandLineTool", "ExpressionTool", "Workflow"]
            ]
        )
