import shlex

from ..langserver.lspobjects import (
    DocumentSymbol, Range, Position, SymbolKind, CompletionItem, CompletionList, Location)
from .process import Process, resolve_file_path

import logging
logger = logging.getLogger(__name__)


class WorkflowCompletions(Process):

    def completions(self, position: Position, snippets: dict):
        p = self._compute_path(position=position)
        return {
            "steps": self._step_completion,
            "inside step": self._inside_step_completion,
            "step_inputs": self._step_input_completion,
            None: self._no_completion
        }.get(self._get_completion_type(p))(p, position, snippets)

    def _get_completion_type(self, p):
        if len(p) and p[-1] == "steps":
            return "steps"

        if len(p) > 1 and p[-2] == "steps":
            return "inside step"

        if len(p) >= 4 and p[-4] == "steps" and p[-3] == "in":
            return "step_inputs"

    def _prefix(self, position: Position):
        pref = self.lines[position.line].split(":", 1)
        return pref[-1].strip()

    def _no_completion(self, path, position: Position, snippets: dict):
        return None

    def _step_completion(self, path, position: Position, snippets: dict):
        return super()._quick_completions(
            position=position, snippets=snippets,
            snippet_keys=["WFStep"])

    def _inside_step_completion(self, path, position: Position, snippets: dict):

        # Linked document file picker
        if self.lines[position.line].lstrip().startswith("run"):
            return [
                CompletionItem(label=file_path)
                for file_path in self._file_picker(self._prefix(position))
            ]

    def _file_picker(self, prefix):

        # We use .split( ... ) so we can handle the case for run: .    # my/commented/path
        # an other such shenanigans
        _prefix = shlex.split(prefix, comments=True)[0]

        path = resolve_file_path(self.doc_uri, _prefix)
        if not path.is_dir():
            path = path.parent

        if not path.exists():
            logger.error(f"No path called: {path}")
            return []

        # This is a workaround to the issue of having a dangling "." in front of the path
        pre = "/" if _prefix in [".", ".."] else ""

        return (pre + str(p.relative_to(path))
                for p in path.iterdir()
                if p.is_dir() or p.suffix == ".cwl")

    def _step_input_completion(self, path, position: Position, snippets: dict):
        return None
