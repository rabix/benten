"""Collection of functions to perform common editing operations on a YAML document.
Meant to be mixin for YamlDoc"""
from typing import Tuple

from .edit import Edit, EditMark
from .lineloader import YNone, LAM


class YamlDocEdit:

    def insert_into_lom(self, path: Tuple[str, ...], key: str, key_field: str, entry: str):
        """Will add new entry or replace existing one. If empty or missing, will prefer map.
        Will create the last path element if needed"""

        if path in self:
            as_list = isinstance(self[path], LAM)
        else:
            as_list = False

        end = None
        text_lines = []

        top_value = self[path[:-1]]
        section_key = path[-1]

        # Quick surgery for docs with no such section or empty section
        if section_key not in top_value:
            # No step field
            text_lines += ["{}:\n".format(section_key)]
            as_list = False

            line_to_insert = top_value.end.line
            column_to_insert = 0
            indent = 2 * " "

        elif isinstance(top_value[section_key], YNone) or len(top_value[section_key]) == 0:
            # Tricky, section is none or empty
            text_lines += ["{}:\n".format(section_key)]
            as_list = False

            line_to_insert = top_value[section_key].start.line
            column_to_insert = 0
            indent = 2 * " "

            # This is the edge case - we need to replace the entire, empty section
            select_end_line = top_value[section_key].end.line
            select_end_column = top_value[section_key].end.column
            end = EditMark(select_end_line, select_end_column)

        elif key in top_value[section_key]:

            sub_sec = top_value[section_key][key]

            line_to_insert = sub_sec.start.line
            column_to_insert = 0
            indent = (sub_sec.start.column - 2) * " "

            # We need to replace the entire section
            select_end_line = sub_sec.end.line
            select_end_column = sub_sec.end.column
            end = EditMark(select_end_line, select_end_column)

        else:
            *_, last_step_id = top_value[section_key].keys()

            line_to_insert = top_value[section_key][last_step_id].end.line
            column_to_insert = 0
            step_line = self.raw_lines[top_value[section_key].start.line]
            indent = (len(step_line) - len(step_line.lstrip())) * " "

        if as_list:
            text_lines += [indent + "- {}: {}\n".format(key_field, key)]
        else:
            text_lines += [indent + "{}:\n".format(key)]

        indent += " " * 2
        text_lines += [indent + l for l in entry.splitlines(keepends=True)]

        start = EditMark(line_to_insert, column_to_insert)
        return Edit(start, end, "".join(text_lines), text_lines)
