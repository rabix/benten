"""This represents a fragment of a CWL document that we can retrieve and edit separately.
It can be an entire CWL document (like the run field of an inlined step), just the documentation
or description part of a CWL or just a one line expression."""
from typing import Tuple, Union
import pathlib
import os
from enum import IntEnum, auto
from abc import abstractmethod

from ..implementationerror import ImplementationError
from .lineloader import (parse_yaml_with_line_info,
                         DocumentError,
                         lookup, reverse_lookup,
                         Ydict, Ylist, Ystr)


class ViewType(IntEnum):
    Process = auto()
    Expression = auto()
    Doc = auto()


def is_expression(value):
    return value.lstrip().startswith("$(") or value.lstrip().startswith("${")


def is_doc_string(key):
    return key in ["doc", "contents"]


class CwlDoc:

    def __init__(self):
        self.raw_cwl = None
        self.parent_view: 'CwlDoc' = None

        self.path = None
        self.inline_path = None
        self.view_type = None

    def synchronize_edit(self, raw_cwl: str, inline_path: Tuple[Union[str, int], ...]=None):
        if self.parent_view is not None:
            return self.parent_view.synchronize_edit(raw_cwl, (self.inline_path or ()) + inline_path)

    def get_rel_path(self, sub_path: pathlib.Path):
        """Path relative to this document e.g. for linked steps"""
        return os.path.relpath(sub_path.absolute(), self.path.absolute().parent)

    def is_deleted(self):
        return self.raw_cwl is None

    # Notice that in the following methods once we get to the parent, nothing happens
    # in this implementation. These are meant to be extended in CwlProcess to actually
    # do something in the parent view

    def status(self):
        if self.parent_view is not None:
            return self.parent_view.status()

    def save(self):
        if self.parent_view is not None:
            return self.parent_view.save()

    def load(self):
        if self.parent_view is not None:
            return self.parent_view.load()

    def propagate_edits(self):
        """Called, from the base, when we have changed something in the raw_cwl"""
        if self.parent_view is not None:
            self.parent_view.propagate_edits()
