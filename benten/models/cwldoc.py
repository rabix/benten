"""Container for storing a CWL object in memory and for applying some edits to it"""
from enum import IntEnum
import pathlib

import yaml


# In [3]: %timeit cwl = blib.CwlDoc(fname=pathlib.Path("salmon.cwl"))
# 28.8 ms ± 832 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)


# From a hint here: https://stackoverflow.com/a/53647080
# This is not suitable for general YAML parsing, but works for our use case
class CLineLoader(yaml.CSafeLoader):

    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        mapping["__meta__"] = {
            "__start_line__": node.start_mark.line,
            "__end_line": node.end_mark.line,
            "__flow__": node.flow_style
        }
        return mapping

    def construct_sequence(self, node, deep=False):
        seq = super().construct_sequence(node, deep=deep)
        seq.append({
            "__start_line__": node.start_mark.line,
            "__end_line": node.end_mark.line,
            "__flow__": node.flow_style
        })
        return seq


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


class CwlDoc:
    def __init__(self, fname: pathlib.Path=None, raw_cwl: str=None):
        if fname is not None:
            self.raw_cwl = fname.open("r").read()
        elif raw_cwl is not None:
            self.raw_cwl = raw_cwl
        else:
            raise ValueError("Need to pass path to CWL or raw CWL string")

        self.cwl_lines = self.raw_cwl.splitlines()
        self.cwl_dict = yaml.load(self.raw_cwl, Loader=CLineLoader)

    def apply_manual_edit(self, raw_cwl: str):
        if self.raw_cwl != raw_cwl:
            self.raw_cwl = raw_cwl
            self.cwl_lines = self.raw_cwl.splitlines()
            self.cwl_dict = yaml.load(self.raw_cwl, Loader=CLineLoader)

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
        self.cwl_dict = yaml.load(self.raw_cwl, Loader=CLineLoader)
