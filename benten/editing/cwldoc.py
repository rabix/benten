"""Stores CWL document in several forms to provide data other classes need for navigation
and manipulation. Importantly, implements logic to extract inline fragments and to apply
edits of inline fragments back to main document."""
from typing import Tuple
import pathlib
import os

from .lineloader import parse_yaml_with_line_info, DocumentError


class CwlDoc:
    def __init__(self, raw_cwl: str, path: pathlib.Path, inline_path: Tuple[str, ...]=None,
                 yaml_error=None):
        self.raw_cwl = raw_cwl
        self.path = path
        self.inline_path = inline_path
        self.cwl_lines = self.raw_cwl.splitlines(keepends=True)
        self.cwl_dict = None
        self.yaml_error = [yaml_error] if yaml_error else []

    def is_invalid(self):
        # We can't possibly have parsed the CWL if we had errors at the YAML level.
        # This is meant for "last known good state" use cases. A client should use
        # this to lockout certain interactions
        return len(self.yaml_error) and self.cwl_dict is not None

    # I want to be conscious and in control of when this (semi)expensive computation is being done
    # But I'd don't want to accidentally do it twice
    def compute_cwl_dict(self):
        if self.cwl_dict is None:
            try:
                self.cwl_dict = parse_yaml_with_line_info(self.raw_cwl, convert_to_lam=True) or {}
            except DocumentError as e:
                self.yaml_error += [e]

    def process_type(self):
        return self.cwl_dict.get("class", "unknown")

    def get_rel_path(self, sub_path: pathlib.Path):
        return os.path.relpath(sub_path.absolute(), self.path.absolute().parent)

    def _get_lines_for_nested_inline_step(self, inline_path: Tuple[str, ...]):
        def _find_step(_doc_dict, _inline_path):
            if len(_inline_path) == 0:
                return _doc_dict
            else:
                for _id, step in _doc_dict["steps"].items():
                    if _id == _inline_path[0]:
                        return _find_step(step["run"], _inline_path[1:])

        if self.inline_path is not None:
            raise RuntimeError("Sub part from nested document fragment is not allowed")

        nested_doc = _find_step(self.cwl_dict, inline_path)

        # Now we have a dict with line numbers, which we'll use to extract from the main doc
        start_line = nested_doc.start.line
        end_line = nested_doc.end.line
        indent_level = len(self.cwl_lines[start_line]) - len(self.cwl_lines[start_line].lstrip())

        return start_line, end_line, indent_level

    # No error checking here because this will be asked for programatically only
    # if the nested dict exists
    def get_raw_cwl_of_nested_inline_step(self, inline_path: Tuple[str, ...]):
        start_line, end_line, indent_level = self._get_lines_for_nested_inline_step(inline_path)
        lines_we_need = self.cwl_lines[start_line:end_line]
        lines = [
            l[indent_level:] if len(l) > indent_level else "\n"
            for l in lines_we_need
        ]
        # All lines with text have the given indent level or more, so they are not an issue
        # Blank lines, however, can be zero length, hence the exception.

        return "".join(lines)

    def get_nested_inline_step(self, inline_path: Tuple[str, ...]):
        if self.is_invalid():
            raise RuntimeError("Can't do edits on invalid document")

        return CwlDoc(raw_cwl=self.get_raw_cwl_of_nested_inline_step(inline_path),
                      path=self.path, inline_path=inline_path)

    def get_raw_cwl_of_base_after_nested_edit(self, inline_path: Tuple[str, ...], new_cwl: str):
        if self.is_invalid():
            raise RuntimeError("Can't do edits on invalid document")

        start_line, end_line, indent_level = self._get_lines_for_nested_inline_step(inline_path)

        new_lines = [((' '*indent_level) if len(l) > 1 else "") + l
                     for l in new_cwl.splitlines(keepends=True)]
        # All lines with text have the given indent level or more, so they are not an issue
        # Blank lines, however, can be zero length, hence the exception.

        self.cwl_lines = self.cwl_lines[:start_line] + new_lines + self.cwl_lines[end_line:]
        return "".join(self.cwl_lines)
