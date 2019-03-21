"""This represents a leaf node in a document, which is plain text"""
from typing import Tuple

from ..implementationerror import ImplementationError


class TextView:

    def __init__(self,
                 raw_text: str,
                 inline_path: Tuple[str, ...]=(),
                 parent: 'TextView'=None):
        self.raw_text, self.raw_lines = None, None
        self.set_raw_text(raw_text)

        self.inline_path = inline_path
        self.parent: 'TextView' = parent

        self.marked_for_deletion = False

    def set_raw_text(self, raw_text):
        self.raw_text = raw_text
        self.raw_lines = raw_text.splitlines(keepends=True)

    def root(self):
        return self.parent.root() if self.parent else self

    def save(self):
        return self.parent.save()

    def saved(self):
        return self.parent.saved()

    def changed_externally(self):
        return self.parent.changed_externally()

    def load(self):
        return self.parent.load()

    def synchronize_text(self):
        return self.root().apply_from_child(self.raw_text, self.inline_path)

    def apply_from_child(self, raw_text: str, inline_path: Tuple[str, ...]):
        raise ImplementationError("Plain text can not have children.")
        # The actual logic has to be implemented in YamlView

    def readable_path(self):
        return ".".join(p for p in self.inline_path if p not in ["steps", "run"])
