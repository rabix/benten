"""Container for storing a CWL object in memory and for applying some edits to it"""
from typing import Tuple
from enum import IntEnum
import pathlib

from benten.editing.listormap import parse_cwl_to_lom


class EditType(IntEnum):
    Insert = 1
    Replace = 2
    Delete = 3


class DocEdit:
    def __init__(self, start_line: int, end_line: int, new_lines: [str], edit_type: EditType):
        self.start_line = start_line
        self.end_line = end_line
        self.new_lines = new_lines
        self.edit_type = edit_type


class InlineChild:
    # Note that start_line and end_line can change
    def __init__(self, parent: "CwlDoc", start_line: int, end_line: int):
        self.parent = parent
        self.start_line = start_line
        self.end_line = end_line

    def apply_child_edit(self):
        pass


class CwlDoc:
    def __init__(self, raw_cwl: str, path: pathlib.Path, inline_path: Tuple[str]=None):
        self.raw_cwl = raw_cwl
        self.path = path
        self.inline_path = inline_path
        self.cwl_lines = self.raw_cwl.splitlines()
        self.cwl_dict = parse_cwl_to_lom(self.raw_cwl)

    def process_type(self):
        return self.cwl_dict.get("class", "unknown")

    def apply_manual_edit(self, raw_cwl: str):
        if self.raw_cwl != raw_cwl:
            self.raw_cwl = raw_cwl
            self.cwl_lines = self.raw_cwl.splitlines()
            self.cwl_dict = parse_cwl_to_lom(self.raw_cwl)

    def apply_programmatic_edit(self, edit: DocEdit):
        if edit.edit_type == EditType.Insert:
            self.cwl_lines = self.cwl_lines[:edit.start_line] + \
                             edit.new_lines + \
                             self.cwl_lines[edit.start_line:]
        elif edit.edit_type == EditType.Replace:
            self.cwl_lines = self.cwl_lines[:edit.start_line] + \
                             edit.new_lines + \
                             self.cwl_lines[edit.end_line:]
        else:
            self.cwl_lines = self.cwl_lines[:edit.start_line] + \
                             self.cwl_lines[edit.end_line:]

        self.raw_cwl = "\n".join(self.cwl_lines)
        self.cwl_dict = parse_cwl_to_lom(self.raw_cwl)

    # No error checking here because this will be asked for programatically only
    # if the nested dict exists
    def get_nested_inline_step(self, inline_path: Tuple[str]):

        def _find_step(_doc_dict, _inline_path):
            if len(_inline_path) == 0:
                return _doc_dict
            else:
                for _id, step in _doc_dict["steps"]:
                    if step["id"] == _inline_path[0]:
                        return _find_step(step["run"], _inline_path[1:])

        if self.inline_path is not None:
            raise RuntimeError("Sub part from nested document fragment is not allowed")

        nested_doc = _find_step(self.cwl_dict, inline_path)

        # Now we have a dict with line numbers, which we'll use to extract from the main doc
        start_line = nested_doc.start_line
        end_line = nested_doc.end_line
        lines_we_need = self.cwl_lines[start_line:end_line]
        indent_level = len(lines_we_need[0]) - len(lines_we_need[0].lstrip())
        lines = [
            l[indent_level:]
            for l in lines_we_need
        ]

        return CwlDoc(raw_cwl="\n".join(lines), path=self.path, inline_path=inline_path)
