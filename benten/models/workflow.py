from .process import Process
from ..langserver.lspobjects import (
    DocumentSymbol, Range, Position, SymbolKind, CompletionList, Location)

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

    def completions(self, position: Position, snippets: dict):
        p = self._compute_path(position=position)
        if len(p) and p[-1] == "steps":
            return super()._quick_completions(
                position=position, snippets=snippets,
                snippet_keys=["WFStep"])

    def definition(self, position: Position, base_uri: str):
        p = self._compute_path(position)
        _location = super()._definition(p, base_uri)
        if _location is None:
            _location = self._definition(p, base_uri)
        return _location

    def symbols(self):
        symb_steps = self._symbols.get("steps", None)
        if symb_steps is None:
            return list(self._symbols.values())

        _steps = self.ydict.get("steps", {})
        if not isinstance(_steps, dict):
            _steps = {}
        symb_steps.children = [
            DocumentSymbol(
                name=k,
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

        return list(self._symbols.values())

    def _definition(self, p, base_uri):
        if p[-1] == "run" and p[-3] == "steps":
            step_uri = self._lookup(p)
            if isinstance(step_uri, str):
                return Location(self._resolve_path(base_uri, step_uri).as_uri())
