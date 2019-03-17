import pathlib

from ..implementationerror import ImplementationError
from ..editing.utils import dictify
from ..editing.lineloader import load_yaml


class WorkflowEditMixin:

    def add_step(self, step_scaffold: str,
                 rel_path: pathlib.Path=None,
                 path: pathlib.Path=None, step_id=None):

        sub_process = {}
        base_step_id = step_id or "new_step"
        if path:
            if not rel_path:
                raise ImplementationError("rel path must be supplied")

            if path.exists():
                sub_process = load_yaml(path.open("r").read())
                base_step_id = sub_process.get("id", path.name.replace("-", "_").replace(" ", "_"))

        step_id = base_step_id
        ctr = 1
        while step_id in self.cwl_doc.yaml.get("steps", {}):
            step_id = "{}_{}".format(base_step_id, str(ctr))
            ctr += 1

        in_ports = list(dictify(sub_process.get("inputs", {})).keys())
        out_ports = list(dictify(sub_process.get("outputs", {})).keys())

        fill_out = {
            "label": step_id,
            "in": "[]" if not in_ports else ("\n" + "\n".join("  {}: []".format(inp) for inp in in_ports)),
            "out": out_ports,
            "run": "{}" if rel_path is None else rel_path
        }

        edit = self.cwl_doc.insert_into_lom(
            path=("steps",),
            key=step_id,
            key_field="id",
            entry=step_scaffold.format(**fill_out)
        )
        return edit
