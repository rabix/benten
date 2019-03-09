import pathlib

from ..editing.utils import dictify
from ..editing.lineloader import load_yaml


class WorkflowEditMixin:

    def add_step(self, path: pathlib.Path=None, step_id=None):

        sub_process = {}
        base_step_id = step_id or "new_step"
        if path:
            if path.exists():
                sub_process = load_yaml(path.open("r").read())
                base_step_id = sub_process.get("id", path.name.replace("-", "_").replace(" ", "_"))

        step_id = base_step_id
        ctr = 1
        while step_id in self.cwl_doc.cwl_dict.get("steps", {}):
            step_id = "{}_{}".format(base_step_id, str(ctr))
            ctr += 1

        in_ports = list(dictify(sub_process.get("inputs", {})).keys())
        out_ports = list(dictify(sub_process.get("outputs", {})).keys())

        edit, text_lines, indent = self.prefix_for_add_subsection(
            section_key="steps",
            sub_section_key=step_id,
            key_field="id",
            prefer_dict=True)

        text_lines += [indent + "  label: {}".format(step_id)]
        text_lines += [indent + "  doc:"]
        text_lines += [indent + "  in: {}".format("" if in_ports else "[]")]
        for inp in in_ports:
            text_lines += [indent + "    {}: []".format(inp)]
        text_lines += [indent + "  out: {}".format(out_ports)]
        if path is None:  # new inline step
            text_lines += [indent + "  run: {}"]
        else:
            text_lines += [indent + "  run: {}".format(self.cwl_doc.get_rel_path(path))]
        text_lines += [indent + "  scatter: "]
        text_lines += [indent + "  scatterMethod: "]
        text_lines += [indent + "  hints: []"]
        text_lines += [indent + "  requirements: []"]

        text_lines += ["\n"]

        # start = EditMark(line_to_insert, column_to_insert)
        # return Edit(start, end, "\n".join(text_lines))
        edit.text = "\n".join(text_lines)
        return edit
