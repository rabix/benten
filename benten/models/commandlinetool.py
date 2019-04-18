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
            "baseCommand": False,
            "requirements": False,
            "hints": False
        }
        self.parse_sections(fields)

    def completions(self, position: Position, snippets: dict):
        p = compute_path(
            doc=self.ydict,
            line=position.line,
            column=position.character
        )
        logger.debug(f"Path at cursor: {p}")

        return CompletionList()
