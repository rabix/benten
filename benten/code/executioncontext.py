"""Manages aspects related to test executions of the CWL and of JS expressions."""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
import random

from ..cwl.lib import un_mangle_uri, list_as_map
from .sampledata import get_sample_runtime, generate_sample_inputs, generate_sample_outputs

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

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
        self._intermediate_outputs = {}

    def runtime(self, doc_path: tuple):
        return get_sample_runtime(self.cwl, doc_path)

    @property
    def job_inputs(self):
        ex_job_file = self.get_sample_data_file_path()
        if not ex_job_file.exists() or ex_job_file.stat().st_size == 0:
            ex_job_file.parent.mkdir(parents=True, exist_ok=True)
            auto_set_inputs = generate_sample_inputs(self.cwl, self.user_types)
            fast_yaml_io.dump(auto_set_inputs, ex_job_file)

        user_set_inputs = {}
        if ex_job_file.exists():
            try:
                user_set_inputs = fast_yaml_io.load(ex_job_file.open().read() or "")
            except (ParserError, ScannerError) as e:
                logger.error(f"Error loading sample input file {ex_job_file}")
        else:
            logger.error(f"No sample input file {ex_job_file}")

        return user_set_inputs

    @property
    def job_outputs(self):
        return generate_sample_outputs(self.cwl, self.user_types)

    def set_expression_lib(self, expression_lib: list=None):
        self.expression_lib = expression_lib

    def get_sample_data_file_path(self) -> pathlib.Path:
        return self.scratch_path / pathlib.Path(
            *un_mangle_uri(self.doc_uri).with_suffix(job_inputs_ext).parts[1:])
