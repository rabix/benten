"""This provides a FE independent layer that takes care of various operations on the workflow.
It wraps on top of the Workflow object and encapsulates the actions module.
Because programmatic edits can be non-local (changes at multiple points in the document) and hard
to predict beforehand (the changes have to be applied to the YAML and then printed out) we avoid
using any intrinsic editor undo/redo stack and have our own."""

import os
import pathlib

import ruamel.yaml.error as rue

import benten.lib as blib
import benten.logic.workflow as WF
import benten.logic.actions as actions
from benten.editing.history import History


class WorkflowEditor:
    def __init__(self, cwl_txt: str, wf_path: pathlib.Path):
        self.wf_path = wf_path
        self.cwl_doc = None
        self.wf: WF.Workflow = None
        self.history = History(cwl_txt)
        self._parse_edit(txt=cwl_txt)

    def as_text(self):
        return self.history.current()

    def redo(self):
        self._parse_edit(txt=self.history.redo())

    def undo(self):
        self._parse_edit(txt=self.history.undo())

    def _parse_edit(self, cwl_doc:WF.CommentedMap=None, txt:str=None):
        if cwl_doc is None:
            try:
                # We can get YAML errors here since this is free text.
                self.cwl_doc = blib.yamlify(txt)
            except rue.YAMLError:
                self.cwl_doc = None
        else:
            self.cwl_doc = cwl_doc
            txt = blib.to_text(self.cwl_doc)

        # We can get CWL errors here
        self.wf = WF.Workflow(self.cwl_doc, self.wf_path)

        return txt

    def _register_an_edit(self, cwl_doc:WF.CommentedMap=None, txt:str=None):
        txt = self._parse_edit(cwl_doc, txt)
        self.history.append(txt)

    def manual_edit(self, txt: str):
        self._register_an_edit(txt=txt)

    def add_wf_input(self, inp_id: str):
        self._register_an_edit(cwl_doc=blib.reyamlify(actions._add_wf_input(self.cwl_doc, inp_id)))

    def add_wf_output(self, outp_id: str):
        self._register_an_edit(cwl_doc=blib.reyamlify(actions._add_wf_output(self.cwl_doc, outp_id)))

    @staticmethod
    def _sanitize_id(txt_id: str):
        if txt_id.endswith(".cwl"):
            txt_id = txt_id[:-4]
        return txt_id.replace("-", "_").replace(".", "_")

    def add_step(self, run_path: pathlib.Path, step_id: str=None):
        _run_path = str(run_path.absolute())

        sub_process = blib.load_cwl(_run_path, round_trip=False)
        candidate_step_id = _step_id = step_id or sub_process.get("id", self._sanitize_id(run_path.name))

        ctr = 1
        while candidate_step_id in blib.lom(self.cwl_doc["steps"]):
            candidate_step_id = _step_id + "_{}".format(ctr)
            ctr += 1

        self._register_an_edit(cwl_doc=blib.reyamlify(actions._add_step(
            self.cwl_doc, os.path.relpath(_run_path, self.wf_path.parent), candidate_step_id)))


