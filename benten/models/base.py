from typing import List

from ..langserver.lspobjects import Diagnostic, Position, CompletionList


class Base:
    def __init__(self, ydict: (dict, str), existing_issues: List[Diagnostic]=None):
        self.ydict = ydict
        self.problems: List[Diagnostic] = existing_issues or []

    def completions(self, position: Position, snippets: dict):
        return CompletionList()
