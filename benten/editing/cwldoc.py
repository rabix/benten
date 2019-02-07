"""Container for storing a CWL object in memory and for applying some edits to it"""
from typing import List, Dict, Generator, Tuple
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
            "__end_line__": node.end_mark.line,
            "__flow__": node.flow_style
        }
        return mapping

    def construct_sequence(self, node, deep=False):
        seq = super().construct_sequence(node, deep=deep)
        seq.append({
            "__start_line__": node.start_mark.line,
            "__end_line__": node.end_mark.line,
            "__flow__": node.flow_style
        })
        return seq


# To be used for toplevel, inputs, outputs, steps, in/out of steps
def list_or_map_w_line_no(lom: (List, Dict)) -> Generator[Tuple[str, object, int, int], None, None]:
    def _get_line_range(_v, _parent_range):
        if not isinstance(_v, dict):
            return _parent_range
        else:
            return _v["__meta__"]["__start_line__"], v["__meta__"]["__end_line__"]

    if isinstance(lom, List):
        for n, v in enumerate(lom[:-1]):
            # CWL demands that these are dicts. And because this is from a list, it has to
            # have an "id" field
            yield (v["id"], v) + _get_line_range(v, (lom[-1]["__start_line__"], lom[-1]["__start_line__"]))
    else:
        for k, v in lom.items():
            if k == "__meta__": continue
            yield (k, v) + _get_line_range(v, (lom["__meta__"]["__start_line__"], lom["__meta__"]["__start_line__"]))


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
    def __init__(self, raw_cwl: str, path: pathlib.Path, inline_path: str=None):
        self.raw_cwl = raw_cwl
        self.path = path
        self.inline_path = inline_path
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

    # No error checking here because this will be asked for programatically only
    # if the nested dict exists
    def get_nested_inline_step(self, inline_path: [str]):

        def _find_step(_doc_dict, _inline_path):
            if len(_inline_path) == 0:
                return _doc_dict
            else:
                for steps in _doc_dict["steps"]:
                    if steps["id"] == _inline_path[0]:
                        return _find_step(steps["run"], _inline_path[1:])

        if self.inline_path is not None:
            raise RuntimeError("Sub part from nested document fragment is not allowed")

        nested_doc = _find_step(self.cwl_dict, inline_path)

        # Now we have a dict with line numbers, which we'll use to extract from the main doc
        meta = nested_doc["meta"]
        lines_we_need = self.cwl_lines[meta["__start_line__"]:meta["__end_line__"]]
        indent_level = len(lines_we_need[0]) - len(lines_we_need[0].lstrip())
        lines = [
            l[indent_level:]
            for l in lines_we_need
        ]

        return CwlDoc(raw_cwl="\n".join(lines), path=self.path, inline_path=inline_path)
