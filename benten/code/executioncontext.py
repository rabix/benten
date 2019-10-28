"""Manages aspects related to test executions of the CWL and of JS expressions."""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from ..cwl.lib import un_mangle_uri, list_as_map
from .sampledata import (
    get_sample_runtime,
    get_sample_data,
    get_sample_globbed_files)

from ruamel.yaml import YAML

import logging
logger = logging.getLogger(__name__)

fast_yaml_io = YAML(typ='safe')
fast_yaml_io.default_flow_style = False

job_inputs_ext = ".benten.test.job.yml"


class ExecutionContext:
    """Carries the job object (sample inputs), expression lib and, if a workflow, simulated
    outputs for each step"""

    def __init__(self, doc_uri: str, cwl: dict, user_types: dict, scratch_path: pathlib.Path):
        self.doc_uri = doc_uri
        self.cwl = cwl
        self.user_types = user_types
        self.scratch_path = scratch_path
        self.expression_lib = []
        self._sample_data = None
        # self._intermediate_outputs = None

    def runtime(self, doc_path: tuple):
        return get_sample_runtime(self.cwl, doc_path)

    @property
    def sample_data(self):
        ex_job_file = self.get_sample_data_file_path()
        if ex_job_file.exists():
            if ex_job_file.open().readline().startswith("#custom"):
                self._sample_data = fast_yaml_io.load(ex_job_file.open().read() or "")
                return self._sample_data

        if self._sample_data is None:
            self._sample_data = get_sample_data(self.doc_uri, self.cwl, self.user_types)
            ex_job_file.parent.mkdir(parents=True, exist_ok=True)
            fast_yaml_io.dump(self._sample_data, ex_job_file)

        return self._sample_data

    def get_workflow_step_inputs(self, doc_path: tuple):
        step_id = doc_path[1]
        step_sample_outputs = self.sample_data["inputs"]
        step_obj = list_as_map(self.cwl.get("steps"), key_field="id", problems=[]).get(step_id)
        input_obj = {}
        for k, in_obj in list_as_map(step_obj.get("in"), key_field="id", problems=[]).items():
            if isinstance(in_obj, dict):
                src = in_obj.get("source")
            else:
                src = in_obj

            if isinstance(src, list):
                input_obj[k] = [step_sample_outputs.get(s) for s in src]
            else:
                input_obj[k] = step_sample_outputs.get(src)

        self_obj = input_obj.get(doc_path[3])

        return input_obj, self_obj

    @staticmethod
    def get_sample_globbed_files(name):
        return get_sample_globbed_files(name)

    def set_expression_lib(self, expression_lib: list=None):
        self.expression_lib = expression_lib

    def get_sample_data_file_path(self) -> pathlib.Path:
        return self.scratch_path / pathlib.Path(
            *un_mangle_uri(self.doc_uri).with_suffix(job_inputs_ext).parts[1:])
