"""This handles the dirty work of interfacing a YAML (CWL) document with the external world,
such as the file system or the Seven Bridges app repository"""
import pathlib
import os

from ..editing.yamlview import YamlView, TextType, EditorInterface


class CwlDoc:

    def __init__(self, file_path: pathlib.Path, editor: EditorInterface):
        self.file_path = file_path
        self.root_view = YamlView(
            raw_text=file_path.open("r").read(),
            text_type=TextType.process,
            editor=editor,
            path=())
        self._last_saved_raw_text = self.root_view.doc.raw_text

    def get_rel_path(self, sub_path: pathlib.Path):
        """Path relative to this document e.g. for linked steps"""
        return os.path.relpath(sub_path.absolute(), self.file_path.absolute().parent)

    def saved(self):
        return self._last_saved_raw_text == self.root_view.doc.raw_text

    def save(self):
        self.file_path.resolve().open("w").write(self.root_view.doc.raw_text)
        self._last_saved_raw_text = self.root_view.doc.raw_text

    def load(self):
        self.root_view.attached_editor.set_text(self.file_path.resolve().open("r").read())
        self.root_view.fetch_from_editor()
        self._last_saved_raw_text = self.root_view.doc.raw_text
