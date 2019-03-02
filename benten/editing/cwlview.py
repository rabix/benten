"""This represents a fragment of a CWL document that we can retrieve and edit separately.
It can be an entire CWL document (like the run field of an inlined step) or just a one line
expression. It's main responsibility is to make sure edits are synchronized across different
views of a document.

Q. What happens if we have a YAML error in any one of the linked views?
A. We should lock the user to that view until the error is fixed

Q. What happens if we delete a child from a parent?
A. The child view is set to none, which indicates to the editor to close that tab

Q. What happens if we clear out all the text from a child?
A. It is replaced with an empty dict, list or string depending on what type the child was

"""
from typing import Tuple
import pathlib
import os
from enum import IntEnum, auto

from .lineloader import parse_yaml_with_line_info, DocumentError, Ydict


class ViewType:
    UnknownTool = auto()
    CommandLineTool = auto()
    ExpressionTool = auto()
    Workflow = auto()
    Expression = auto()
    Doc = auto()


class CwlView:
    def __init__(self,
                 raw_cwl: str,
                 path: pathlib.Path=None, inline_path: Tuple[(str, int), ...]=None,
                 view_type: ViewType=None,
                 parent_view: 'CwlView'=None,
                 previous_view: 'CwlView'=None):

        self.raw_cwl = None
        self.last_saved_raw_cwl = None
        self.cwl_lines = None
        self.cwl_dict = None
        self.yaml_error = None

        self.parent_view = parent_view
        self.child_views = []

        if previous_view is not None:
            self.path = previous_view.path
            self.inline_path = previous_view.inline_path
            self.view_type = previous_view.view_type
            self.last_known_good_dict = previous_view.last_known_good_dict
        else:
            self.path = path
            self.inline_path = inline_path
            self.view_type = view_type
            self.last_known_good_dict = None

        self.set_raw_cwl(raw_cwl, saved=True)

    def set_raw_cwl(self, raw_cwl, saved=False):
        self.raw_cwl = raw_cwl
        self.last_saved_raw_cwl = raw_cwl if saved else None
        self.cwl_lines = self.raw_cwl.splitlines(keepends=True)
        self.cwl_dict = None
        self.yaml_error = None

    def is_invalid(self):
        return self.yaml_error is not None

    # I want to be conscious and in control of when this (semi)expensive computation is being done
    # But I'd don't want to accidentally do it twice
    def compute_cwl_dict(self):
        if self.cwl_dict is None:
            try:
                self.cwl_dict = parse_yaml_with_line_info(self.raw_cwl, convert_to_lam=True) or {}
                self.last_known_good_dict = self.cwl_dict
            except DocumentError as e:
                self.yaml_error = e

    def type(self):
        if self.view_type == ViewType.Process:
            return self.cwl_dict.get("class", "unknown")
        else:
            return

    def get_rel_path(self, sub_path: pathlib.Path):
        return os.path.relpath(sub_path.absolute(), self.path.absolute().parent)

    def status(self):
        if self.parent_view is not None:
            return self.parent_view.status()

        _status = {
            "changed_externally": False,
            "saved": False
        }

        raw_cwl_on_disk = self.path.resolve().open("r").read()

        if raw_cwl_on_disk != self.last_saved_raw_cwl:
            _status["changed_externally"] = True
        elif raw_cwl_on_disk == self.raw_cwl:
            _status["saved"] = True

        return _status

    def save(self):
        if self.parent_view is not None:
            return self.parent_view.save()

        self.path.resolve().open("w").write(self.raw_cwl)
        self.last_saved_raw_cwl = self.raw_cwl

    def load(self):
        if self.parent_view is not None:
            return self.parent_view.load()

        self.set_raw_cwl(raw_cwl=self.path.resolve().open("r").read(), saved=True)

    def register_edit(self, raw_cwl):
        self.set_raw_cwl(raw_cwl=raw_cwl)

        if self.parent_view is None:
            self.compute_cwl_dict()
            for child_view in self.child_views:
                child_view.set_raw_cwl(raw_cwl=self.get_view_for(child_view))
        else:
            self.parent_view.propagate_edits(self)

    def get_view_for(self, child_view: 'CwlView'):
        if self.parent_view is not None:
            return self.parent_view.get_view_for(child_view)

