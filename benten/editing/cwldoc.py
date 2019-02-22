"""Stores CWL document in several forms to provide data other classes need for navigation
and manipulation. Importantly, implements logic to extract inline fragments and to apply
edits of inline fragments back to main document."""
from typing import Tuple
from enum import IntEnum
import pathlib

from .listormap import parse_cwl_to_lom
from .lineloader import parse_yaml_with_line_info, Ydict, Ylist
from .listasmap import lom


# We've flattened them all together. The names don't clash (due to inheritance), so we are ok
# if we run into trouble, we'll have to add context information (CWL type, parent type etc.)
allowed_loms = {
    "inputs": "id",
    "outputs": "id",
    "requirements": "class",
    "hints": "class",
    "fields": "name",
    "steps": "id",
    "in": "id"
}


def _recurse_convert_lam(doc: (Ydict, Ylist)):
    if isinstance(doc, Ylist):
        for v in doc:
            _recurse_convert_lam(v)
    elif isinstance(doc, Ydict):
        for k, v in doc.items():
            if k in allowed_loms:
                doc[k] = lom(v)
            _recurse_convert_lam(v)
    else:
        return doc


class CwlDoc:
    def __init__(self, raw_cwl: str, path: pathlib.Path, inline_path: Tuple[str, ...]=None):
        self.raw_cwl = raw_cwl
        self.path = path
        self.inline_path = inline_path
        self.cwl_lines = self.raw_cwl.splitlines(keepends=True)
        self.cwl_dict = None

    # I want to be conscious and in control of when this (semi)expensive computation is being done
    # But I'd don't want to accidentally do it twice
    def compute_cwl_dict(self):
        if self.cwl_dict is None:
            self.cwl_dict = parse_yaml_with_line_info(self.raw_cwl)
            _recurse_convert_lam(self.cwl_dict)

    def process_type(self):
        return self.cwl_dict.get("class", "unknown")

    def _get_lines_for_nested_inline_step(self, inline_path: Tuple[str, ...]):
        def _find_step(_doc_dict, _inline_path):
            if len(_inline_path) == 0:
                return _doc_dict
            else:
                for _id, step in lom(_doc_dict["steps"]).items():
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
        return CwlDoc(raw_cwl=self.get_raw_cwl_of_nested_inline_step(inline_path),
                      path=self.path, inline_path=inline_path)

    def get_raw_cwl_of_base_after_nested_edit(self, inline_path: Tuple[str, ...], new_cwl: str):
        start_line, end_line, indent_level = self._get_lines_for_nested_inline_step(inline_path)

        new_lines = [((' '*indent_level) if len(l) > 1 else "") + l
                     for l in new_cwl.splitlines(keepends=True)]
        # All lines with text have the given indent level or more, so they are not an issue
        # Blank lines, however, can be zero length, hence the exception.

        self.cwl_lines = self.cwl_lines[:start_line] + new_lines + self.cwl_lines[end_line:]
        return "".join(self.cwl_lines)


