from .process import Process, Position
from .lineloader import compute_path
from ..langserver.lspobjects import CompletionList, CompletionItem

import logging
logger = logging.getLogger(__name__)


class CommandLineTool(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = {
            "class": True,
            "cwlVersion": True,
            "id": False,
            "doc": False,
            "label": False,
            "inputs": True,
            "outputs": True,
            "stdout": False,
            "baseCommand": False,
            "arguments": False,
            "requirements": False,
            "hints": False
        }
        self.parse_sections(fields)

    def completions(self, position: Position, snippets: dict):
        return CompletionList()
