import pathlib

from ..editing.utils import dictify
from ..editing.lineloader import load_yaml, LAM
from ..editing.edit import Edit, EditMark


class WorkflowEditMixin:

    def add_step(self, path: pathlib.Path):

        sub_process = load_yaml(path.open("r").read())
        base_step_id = sub_process.get("id", path.name.replace("-", "_").replace(" ", "_"))
        step_id = base_step_id
        ctr = 1
        while step_id in self.cwl_doc.cwl_dict.get("steps", {}):
            step_id = "{}_{}".format(base_step_id, str(ctr))
            ctr += 1

        in_ports = list(dictify(sub_process.get("inputs", {})).keys())
        out_ports = list(dictify(sub_process.get("outputs", {})).keys())
        end = None # Usually we just insert the text, but there is an edge case ...

        text_lines = []
        as_list = isinstance(self.cwl_doc.cwl_dict.get("steps"), LAM)

        # Quick surgery for docs with no steps or empty steps
        if "steps" not in self.cwl_doc.cwl_dict:
            # No step field
            text_lines += ["steps:"]
            as_list = False

            line_to_insert = self.cwl_doc.cwl_dict.end.line
            column_to_insert = 0
            indent = 2 * " "

        elif len(self.cwl_doc.cwl_dict["steps"]) == 0:
            # Tricky, steps is empty
            text_lines += ["steps:"]
            as_list = False

            line_to_insert = self.cwl_doc.cwl_dict["steps"].start.line
            column_to_insert = 0 # self.cwl_doc.cwl_dict["steps"].end.column
            indent = 2 * " "

            # This is the edge case - we need to replace the entire, empty steps field
            select_end_line = self.cwl_doc.cwl_dict["steps"].end.line
            select_end_column = self.cwl_doc.cwl_dict["steps"].end.column
            end = EditMark(select_end_line, select_end_column)

        else:
            *_, last_step_id = self.cwl_doc.cwl_dict["steps"].keys()

            line_to_insert = self.cwl_doc.cwl_dict["steps"][last_step_id].end.line
            column_to_insert = 0
            step_line = self.cwl_doc.cwl_lines[self.cwl_doc.cwl_dict["steps"].start.line]
            indent = (len(step_line) - len(step_line.lstrip())) * " "

        if as_list:
            text_lines += [indent + "- id: {}".format(step_id)]
        else:
            text_lines += [indent + "{}:".format(step_id)]

        text_lines += [indent + "  in: {}".format("" if in_ports else "[]")]
        for inp in in_ports:
            text_lines += [indent + "    {}: []".format(inp)]
        text_lines += [indent + "  out: {}".format(out_ports)]
        text_lines += [indent + "  run: {}\n\n".format(self.cwl_doc.get_rel_path(path))]

        start = EditMark(line_to_insert, column_to_insert)
        return Edit(start, end, "\n".join(text_lines))
