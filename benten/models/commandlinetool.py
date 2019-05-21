from .process import Process, Position
from .lineloader import compute_path
from ..langserver.lspobjects import CompletionList, CompletionItem

import logging
logger = logging.getLogger(__name__)


class CommandLineTool(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def completions(self, position: Position, snippets: dict):
        p = self._compute_path(position=position)
        return CompletionList()

    def graph(self):
        _id = self._symbols.get("id")
        _label = self._symbols.get("label")
        if _label is not None:
            label = _label.name
        elif _id is not None:
            label = _id
        else:
            label = "CommandLineTool"

        return {
            "nodes": [{"id": 1, "label": label}],
            "edges": []
        }
