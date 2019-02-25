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
        while step_id in self.cwl_doc.cwl_dict["steps"]:
            step_id = "{}_{}".format(base_step_id, str(ctr))
            ctr += 1

        in_ports = list(dictify(sub_process.get("inputs", {})).keys())
        out_ports = list(dictify(sub_process.get("outputs", {})).keys())

        *_, last_step_id = self.cwl_doc.cwl_dict["steps"].keys()
        line_to_insert = self.cwl_doc.cwl_dict["steps"][last_step_id].end.line
        column_to_insert = 0

        text_lines = []
        as_list = isinstance(self.cwl_doc.cwl_dict["steps"], LAM)
        if as_list:
            text_lines += ["  - id: {}".format(step_id)]
        else:
            text_lines += ["  {}:".format(step_id)]

        text_lines += ["    in: {}".format("" if in_ports else "[]")]
        for inp in in_ports:
            text_lines += ["      {}: []".format(inp)]
        text_lines += ["    out: {}".format(out_ports)]
        text_lines += ["    run: {}\n\n".format(self.cwl_doc.get_rel_path(path))]

        start = EditMark(line_to_insert, column_to_insert)
        end = None
        return Edit(start, end, "\n".join(text_lines))
