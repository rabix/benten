from ..langserver.lspobjects import (
    DocumentSymbol, Range, Position, SymbolKind, CompletionList, Location)
from .process import Process, resolve_file_path


class WorkflowCompletions(Process):

    def completions(self, position: Position, snippets: dict):
        p = self._compute_path(position=position)
        return {
            "steps": self._step_completion,
            "step_inputs": self._step_input_completion,
            None: self._no_completion
        }.get(self._get_completion_type(p))(position, snippets)

    def _get_completion_type(self, p):
        if len(p) and p[-1] == "steps":
            return "steps"

        if len(p) >= 4 and p[-4] == "steps" and p[-3] == "in":
            return "step_inputs"

    def _no_completion(self, position: Position, snippets: dict):
        return None

    def _step_completion(self, position: Position, snippets: dict):
        return super()._quick_completions(
            position=position, snippets=snippets,
            snippet_keys=["WFStep"])

    def _step_input_completion(self, position: Position, snippets: dict):
        return None
