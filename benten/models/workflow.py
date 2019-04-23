from .process import Process
from ..langserver.lspobjects import DocumentSymbol, Range, Position, SymbolKind, CompletionList

import logging
logger = logging.getLogger(__name__)


class Workflow(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields = {
            "class": True,
            "cwlVersion": True,
            "id": False,
            "doc": False,
            "label": False,
            "inputs": True,
            "outputs": True,
            "steps": True,
            "requirements": False,
            "hints": False
        }
        self.parse_sections(self.fields)

    def symbols(self):
        symb = super().symbols()
        symb_steps = next((sy for sy in symb if sy.detail == "steps"), None)
        if symb_steps is None:
            return symb

        _steps = self.ydict.get("steps", {})
        if not isinstance(_steps, dict):
            _steps = {}
        symb_steps.children = [
            DocumentSymbol(
                name=k,
                detail="step",
                kind=SymbolKind.Field,
                _range=Range(
                    start=Position(v.start.line, v.start.column),
                    end=Position(v.end.line, v.end.column)
                ),
                selection_range=Range(
                    start=Position(v.start.line, v.start.column),
                    end=Position(v.end.line, v.end.column)
                )
            )
            for k, v in _steps.items()
        ]

        return symb

    def completions(self, position: Position, snippets: dict):
        p = self._compute_path(position=position)
        if p[0] == "steps":
            return super()._quick_completions(
                position=position, snippets=snippets,
                snippet_keys=["WFStep"])
