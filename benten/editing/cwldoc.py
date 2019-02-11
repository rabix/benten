"""Container for storing a CWL object in memory and for applying some edits to it"""
from typing import Tuple
from enum import IntEnum
import pathlib

from benten.editing.listormap import parse_cwl_to_lom


class EditType(IntEnum):
    Insert = 1
    Replace = 2
    Delete = 3


class CwlDoc:
    def __init__(self, raw_cwl: str, path: pathlib.Path, inline_path: Tuple[str, ...]=None):
        self.raw_cwl = raw_cwl
        self.path = path
        self.inline_path = inline_path
        self.cwl_lines = self.raw_cwl.splitlines()
        self.cwl_dict = parse_cwl_to_lom(self.raw_cwl)

    def process_type(self):
        return self.cwl_dict.get("class", "unknown")

    def _get_lines_for_nested_inline_step(self, inline_path: Tuple[str, ...]):
        def _find_step(_doc_dict, _inline_path):
            if len(_inline_path) == 0:
                return _doc_dict
            else:
                for _id, step in _doc_dict["steps"]:
                    if _id == _inline_path[0]:
                        return _find_step(step["run"], _inline_path[1:])

        if self.inline_path is not None:
            raise RuntimeError("Sub part from nested document fragment is not allowed")

        nested_doc = _find_step(self.cwl_dict, inline_path)

        # Now we have a dict with line numbers, which we'll use to extract from the main doc
        start_line = nested_doc.start_line
        end_line = nested_doc.end_line
        indent_level = len(self.cwl_lines[start_line]) - len(self.cwl_lines[start_line].lstrip())

        return start_line, end_line, indent_level

    # No error checking here because this will be asked for programatically only
    # if the nested dict exists
    def get_nested_inline_step(self, inline_path: Tuple[str, ...]):
        if self.inline_path is not None:
            raise RuntimeError("Sub part from nested document fragment is not allowed")

        start_line, end_line, indent_level = self._get_lines_for_nested_inline_step(inline_path)
        lines_we_need = self.cwl_lines[start_line:end_line]
        lines = [
            l[indent_level:]
            for l in lines_we_need
        ]

        return CwlDoc(raw_cwl="\n".join(lines), path=self.path, inline_path=inline_path)

    def get_raw_cwl_of_base_after_nested_edit(self, inline_path: Tuple[str, ...], new_cwl: str):
        if self.inline_path is not None:
            raise RuntimeError("Nested edits can only be applied to base document")

        start_line, end_line, indent_level = self._get_lines_for_nested_inline_step(inline_path)

        new_lines = [' '*indent_level + l for l in new_cwl.splitlines()]
        self.cwl_lines = self.cwl_lines[:start_line] + new_lines + self.cwl_lines[end_line:]
        return "\n".join(self.cwl_lines)
