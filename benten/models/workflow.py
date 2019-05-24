#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .process import Process, resolve_file_path
from .workflowstructure import WorkflowStructure
from .workflowcompletions import WorkflowCompletions
from ..langserver.lspobjects import (
    DocumentSymbol, Range, Position, SymbolKind, CompletionList, Location)

import logging
logger = logging.getLogger(__name__)


class Workflow(WorkflowCompletions, WorkflowStructure, Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_steps_to_symbol_list()

    def definition(self, position: Position):
        p = self._compute_path(position)
        return super()._definition(p) or self._definition(p)

    def _add_steps_to_symbol_list(self):
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

    def _definition(self, p):
        if len(p) > 2:
            if p[-1] == "run" and p[-3] == "steps":
                step_uri = self._lookup(p)
                if isinstance(step_uri, str):
                    return Location(resolve_file_path(self.doc_uri, step_uri).as_uri())
