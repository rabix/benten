from typing import Tuple, Dict, Callable
from enum import IntEnum

from ..implementationerror import ImplementationError
from .lineloader import parse_yaml_with_line_info, YNone, Ystr, Ydict, DocumentError, LAM
from .edit import Edit, EditMark
from .textview import TextView


class YamlView(TextView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._yaml = None
        self._last_good_yaml = None
        self.yaml_error = None

    @property
    def yaml(self):
        if self._yaml is None:
            try:
                self._yaml = parse_yaml_with_line_info(self.raw_text, convert_to_lam=True) or Ydict.empty()
                self.yaml_error = None
                self._last_good_yaml = self._yaml
            except DocumentError as e:
                self._yaml = None
                self.yaml_error = e
        return self._yaml

    def __contains__(self, path: Tuple[str, ...]):
        sub_doc = self.yaml
        for p in path or []:
            if not isinstance(sub_doc, dict):
                return False
            if p in sub_doc:
                sub_doc = sub_doc[p]
            else:
                return False
        else:
            return True

    def __getitem__(self, path: Tuple[str, ...]):
        sub_doc = self.yaml
        for p in path or []:
            if sub_doc is None:
                raise ImplementationError("Component can not be None.")
            if not isinstance(sub_doc, dict):
                raise ImplementationError("We've got a bad path into a document.")
            sub_doc = sub_doc[p]
        return sub_doc

    def set_raw_text(self, raw_text):
        super().set_raw_text(raw_text)
        self._yaml = None

    def create_child_view(
            self, child_path: Tuple[str, ...],
            can_have_children=False,
            edit_callback: Callable=None,
            delete_callback: Callable=None):
        return self.root().create_child_view(
            child_path=self.inline_path + child_path,
            can_have_children=can_have_children,
            edit_callback=edit_callback,
            delete_callback=delete_callback)

    def add_or_replace_lom(self, path: Tuple[str, ...], key: str, key_field: str, entry: str):
        self.root().add_or_replace_lom(
            path=self.inline_path + path, key=key, key_field=key_field, entry=entry)
