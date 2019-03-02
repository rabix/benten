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

Q. What happens if we have an expression view and in the parent we change that to a scalar (str, int)
A. The child view is set to none, which indicates to the editor to close that tab

Q. What happens if we are editing in one view, and an external edit (that is reloaded) has a YAML
   error?
A. We refuse to reload and warn the user that an external edit would result in a YAML error
   and that error should be fixed, either by saving this workign document, or fixing the document
   in the original external editor.
"""
from typing import Tuple, Union
import pathlib
import os
from enum import IntEnum, auto

from ..implementationerror import ImplementationError
from .lineloader import parse_yaml_with_line_info, DocumentError, lookup, Ydict, Ylist


class ViewType(IntEnum):
    UnknownTool = auto()
    CommandLineTool = auto()
    ExpressionTool = auto()
    Workflow = auto()
    Expression = auto()
    Doc = auto()


def is_expression(value):
    return value.lstrip().startswith("$(") or value.lstrip().startswith("${")


def is_doc_string(key):
    return key in ["doc", "contents"]


class CwlView:
    def __init__(self,
                 raw_cwl: str,
                 path: pathlib.Path=None, inline_path: Tuple[Union[str, int], ...]=None,
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
            if self.view_type is None: raise RuntimeError("View type must be set.")
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

    def is_deleted(self):
        return self.raw_cwl is None

    # I want to be conscious and in control of when this (semi)expensive computation is being done
    # But I'd don't want to accidentally do it twice
    def compute_cwl_dict(self):
        if self.cwl_dict is not None:
            return

        try:
            self.cwl_dict = parse_yaml_with_line_info(self.raw_cwl, convert_to_lam=True) or {}
        except DocumentError as e:
            self.yaml_error = e
            return

        self.last_known_good_dict = self.cwl_dict
        if self.view_type in [ViewType.Expression, ViewType.Doc]:
            return

        self.view_type = {
            "CommandLineTool": ViewType.CommandLineTool,
            "ExpressionTool": ViewType.ExpressionTool,
            "Workflow": ViewType.Workflow
        }.get(self.cwl_dict.get("class"), ViewType.UnknownTool)

    def type(self):
        if self.view_type == ViewType.Process:
            return self.cwl_dict.get("class", "unknown")
        else:
            return

    def get_rel_path(self, sub_path: pathlib.Path):
        """Relative path to put for linked sub processes"""
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
                child_view.set_raw_cwl(raw_cwl=self.get_raw_cwl_for(child_view))
        else:
            self.parent_view.propagate_edits(self)

    def get_raw_cwl_for(self, child_view: 'CwlView'):
        if self.parent_view is not None:
            return self.parent_view.get_raw_cwl_for(child_view)

        try:
            value = lookup(self.cwl_dict, child_view.inline_path)
            key = child_view.inline_path[-1]
        except (KeyError, IndexError) as e:
            # We assume here that we never make an error in the path
            # and a missing element has merely been deleted in a parent edit
            return None

        if not isinstance(value, (Ylist, Ydict)):
            # This has to be a doc or an expression, to start with
            if child_view.view_type not in [ViewType.Expression, ViewType.Doc]:
                raise ImplementationError("This view has an error.")

            # This has to be either an Expression or a doc field



    def open_new_view_at(self, line, col, originating_child: 'CwlView'=None):
        if self.parent_view is not None:
            self.parent_view.open_new_view_at(line, col, originating_child)




    def propagate_edits(self, child_view: 'CwlView'):
        pass

