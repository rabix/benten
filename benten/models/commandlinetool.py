from ..editing.lineloader import compute_path
from .base import Base

import logging
logger = logging.getLogger(__name__)


class CommandLineTool(Base):

    autocomplete_dict = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = (self.cwl_doc.yaml or {}).get("id", None)

        required_sections = ["cwlVersion", "class", "inputs", "outputs"]
        self.parse_sections(required_sections)

    def get_auto_completions(self, line, column, prefix):
        path = compute_path(self.cwl_doc.yaml, line, column)
        logger.debug(f"Cursor at: ({line}, {column}): {path}, prefix: {prefix}")
        trace_path(self.cwl_doc.yaml)
        if not path:
            return []

        if len(path) < 3:
            if path[0] == "inputs":
                return [Base._auto_complete_snippets.get("Input")]

            if path[0] == "requirements":
                return [Base._auto_complete_snippets.get("DockerRequirement")]

        return []


def trace_path(doc, path=(), off=0):

    if not isinstance(doc, (dict, list)):
        return

    values = doc.items() if isinstance(doc, dict) else enumerate(doc)
    for k, v in values:
        print("{}: ({}, {}) - ({}, {})".format(path + (k,),
                                               v.start.line + off, v.start.column,
                                               v.end.line + off, v.end.column))
        trace_path(v, path + (k,), off)
