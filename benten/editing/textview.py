"""This represents a leaf node in a document, which is plain text"""
from typing import Tuple

from ..implementationerror import ImplementationError


class TextView:

    def __init__(self,
                 raw_text: str,
                 inline_path: Tuple[str, ...]=(),
                 parent: 'TextView'=None,
                 edit_callback=None,
                 delete_callback=None):
        self.raw_text, self.raw_lines = None, None

        self.edit_callback = edit_callback
        # This function is called whenever the text is changed via set_raw_text
        self.delete_callback = delete_callback
        # This function is called whenever a view gets deleted

        self.set_raw_text(raw_text)

        self.inline_path = inline_path
        self.parent: 'TextView' = parent

        self.marked_for_deletion = False

    def set_raw_text(self, raw_text):
        self.raw_text = raw_text
        self.raw_lines = raw_text.splitlines(keepends=True)
        if self.edit_callback is not None:
            self.edit_callback(self.raw_text)

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

    def mark_for_deletion(self):
        self.marked_for_deletion = True
        if self.delete_callback is not None:
            self.delete_callback()

    def readable_path(self):
        return self.root().readable_path() + ":" + \
               ".".join(p for p in self.inline_path if p not in ["steps", "run"])
