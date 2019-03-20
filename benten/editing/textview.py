"""This represents a leaf node in a document, which is plain text"""
import pathlib
from typing import Tuple

from ..implementationerror import ImplementationError


class TextView:

    def __init__(self,
                 raw_text: str,
                 file_path: pathlib.Path=None, inline_path: Tuple[str, ...]=(),
                 parent: 'TextView'=None):
        self.raw_text, self.raw_lines = None, None
        self.set_raw_text(raw_text)
        self._last_saved_raw_text = self.raw_text

        self.file_path = file_path
        self.inline_path = inline_path
        self.parent: 'TextView' = parent

        self.marked_for_deletion = False

    def set_raw_text(self, raw_text):
        self.raw_text = raw_text
        self.raw_lines = raw_text.splitlines(keepends=True)

    def root(self):
        return self.parent.root() if self.parent else self

    def save(self):
        if self.parent is not None:
            return self.parent.save()
        else:
            self.file_path.resolve().open("w").write(self.raw_text)
            self._last_saved_raw_text = self.raw_text

    def saved(self):
        if self.parent is not None:
            return self.parent.saved()
        else:
            return self._last_saved_raw_text == self.raw_text

    def load(self):
        if self.parent is not None:
            return self.parent.load()
        else:
            self.set_raw_text(raw_text=self.file_path.resolve().open("r").read())
            self._last_saved_raw_text = self.raw_text

    def project_to_parent(self):
        if self.parent is not None:
            return self.root().apply_from_child(self.raw_text, self.inline_path)
        # The actual logic has to be implemented in YamlView

    def apply_from_child(self, raw_text: str, inline_path: Tuple[str, ...]):
        raise ImplementationError("Plain text can not have children.")
