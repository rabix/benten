import pathlib

from ..editing.utils import dictify
from ..editing.lineloader import load_yaml, LAM, YNone
from ..editing.edit import Edit, EditMark


class EditMixin:

    def prefix_for_add_subsection(self, section_key, sub_section_key, key_field, prefer_dict=True):
        text_lines = []
        as_list = isinstance(self.cwl_doc.cwl_dict.get(section_key), LAM)
        end = None

        # Quick surgery for docs with no such section or empty section
        if section_key not in self.cwl_doc.cwl_dict:
            # No step field
            text_lines += ["{}:".format(section_key)]
            as_list = not prefer_dict

            line_to_insert = self.cwl_doc.cwl_dict.end.line
            column_to_insert = 0
            indent = 2 * " "

        elif isinstance(self.cwl_doc.cwl_dict[section_key], YNone) or len(self.cwl_doc.cwl_dict[section_key]) == 0:
            # Tricky, section is none or empty
            text_lines += ["{}:".format(section_key)]
            as_list = not prefer_dict

            line_to_insert = self.cwl_doc.cwl_dict[section_key].start.line
            column_to_insert = 0
            indent = 2 * " "

            # This is the edge case - we need to replace the entire, empty section
            select_end_line = self.cwl_doc.cwl_dict[section_key].end.line
            select_end_column = self.cwl_doc.cwl_dict[section_key].end.column
            end = EditMark(select_end_line, select_end_column)

        elif sub_section_key in self.cwl_doc.cwl_dict[section_key]:

            sub_sec = self.cwl_doc.cwl_dict[section_key][sub_section_key]

            line_to_insert = sub_sec.start.line
            column_to_insert = 0
            indent = (sub_sec.start.column - 2) * " "

            # This is the edge case - we need to replace the entire, empty section
            select_end_line = sub_sec.end.line
            select_end_column = sub_sec.end.column
            end = EditMark(select_end_line, select_end_column)

        else:
            *_, last_step_id = self.cwl_doc.cwl_dict[section_key].keys()

            line_to_insert = self.cwl_doc.cwl_dict[section_key][last_step_id].end.line
            column_to_insert = 0
            step_line = self.cwl_doc.cwl_lines[self.cwl_doc.cwl_dict[section_key].start.line]
            indent = (len(step_line) - len(step_line.lstrip())) * " "

        if as_list:
            text_lines += [indent + "- {}: {}".format(key_field, sub_section_key)]
            indent += " " * 2
        else:
            text_lines += [indent + "{}:".format(sub_section_key)]

        start = EditMark(line_to_insert, column_to_insert)
        return Edit(start, end, ""), text_lines, indent
        # Note that this is an incomplete edit and has a list of lines. It's meant to be followed
        # by more code that adds more lines as needed and then generate the final edit

