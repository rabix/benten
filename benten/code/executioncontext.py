"""Manages aspects related to test executions of the CWL and of JS expressions."""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
import random

from ..cwl.lib import un_mangle_uri, list_as_map

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

import logging
logger = logging.getLogger(__name__)

fast_yaml_io = YAML(typ='safe')
fast_yaml_io.default_flow_style = False

job_inputs_ext = ".benten.test.job.yml"


class ExecutionContext:
    """Carries the job object (sample inputs) and expression lib for this process"""

    def __init__(self, doc_uri: str, cwl: dict, user_types: dict, scratch_path: pathlib.Path):
        self.doc_uri = doc_uri
        self.cwl = cwl
        self.user_types = user_types
        self.scratch_path = scratch_path
        self.runtime = {
            "outdir": "/out/dir",
            "tmpdir": "/tmp/dir",
            "cores": 4,
            "ram": 1024,
            "outdirSize": 2048,
            "tmpdirSize": 4096
        }
        self.expression_lib = []

    @property
    def job_inputs(self):
        ex_job_file = self.get_sample_data_file_path()
        if not ex_job_file.exists() or ex_job_file.stat().st_size == 0:
            self.set_job_inputs()

        user_set_inputs = {}
        if ex_job_file.exists():
            try:
                user_set_inputs = fast_yaml_io.load(ex_job_file.open().read() or "")
            except (ParserError, ScannerError) as e:
                logger.error(f"Error loading sample input file {ex_job_file}")
        else:
            logger.error(f"No sample input file {ex_job_file}")

        return user_set_inputs

    def set_job_inputs(self):
        ex_job_file = self.get_sample_data_file_path()
        ex_job_file.parent.mkdir(parents=True, exist_ok=True)

        _inputs = self.cwl.get("inputs")
        if not isinstance(_inputs, (list, dict)):
            _inputs = {}
        auto_set_inputs = {
            k: example_value(k, _type_v, self.user_types)
            for k, _type_v in list_as_map(_inputs, key_field="id", problems=[]).items()
        }

        fast_yaml_io.dump(auto_set_inputs, ex_job_file)

    def set_expression_lib(self, expression_lib: list=None):
        self.expression_lib = expression_lib

    def get_sample_data_file_path(self) -> pathlib.Path:
        return self.scratch_path / pathlib.Path(
            *un_mangle_uri(self.doc_uri).with_suffix(job_inputs_ext).parts[1:])


def basic_example_value(name, _type):
    if _type == 'null':
        return 'null'
    elif _type == 'Any':
        return 'Any'
    elif _type == 'boolean':
        return random.randint(0, 1) > 0
    elif _type == 'int' or _type == 'long':
        return random.randint(-1000, 1000)
    elif _type == 'float' or _type == 'double':
        return random.random() * 100 - 50
    elif _type == 'string':
        return name
    elif _type == 'File':
        return {
            'class': 'File',
            'path': f'/path/to/{name}.ext',
            'location': f'/location/of/{name}.ext',
            'basename': f'{name}.ext',
            'dirname': '/path/to/',
            'nameroot': name,
            'nameext': '.ext',
            'checksum': "sha1$deadbeef",
            'size': random.randint(0, 4096),
            'format': 'someformat',
            'contents': 'To be, or not to be. That is the question.'
        }
    elif _type == 'Directory':
        return {
            'class': 'Directory',
            'path': f'/path/to/{name}'
        }


def enum_example_value(symbols):
    return symbols[random.randint(0, len(symbols) - 1)]


def record_example_value(name, _type, user_types):
    return {
        k: example_value(name, _type_v, user_types)
        for k, _type_v in list_as_map(_type.get("fields"), key_field="name", problems=[]).items()
    }


def example_value(name, cwl_type, user_types, array_of=False):
    if array_of:
        return [example_value(name + "/" + str(i), cwl_type, user_types) for i in range(4)]

    if isinstance(cwl_type, list):
        l = len(cwl_type)
        return example_value(name, cwl_type[random.randint(0, l - 1)], user_types)

    elif isinstance(cwl_type, dict) and "type" in cwl_type:
        _type = cwl_type.get("type")
        if _type == "array":
            return example_value(name, cwl_type.get("items"), user_types, array_of=True)
        elif _type == "enum":
            return enum_example_value(cwl_type.get("symbols"))
        elif _type == "record":
            return record_example_value(name, cwl_type, user_types)
        else:
            return example_value(name, _type, user_types)

    elif isinstance(cwl_type, str):
        # desugar
        if cwl_type.endswith("?"):
            cwl_type = cwl_type[:-1]

        if cwl_type.endswith("[]"):
            cwl_type = {
                "type": "array",
                "items": [cwl_type[:-2]]
            }
            return example_value(name, cwl_type, user_types)

        if cwl_type in user_types:
            return example_value(name, user_types.get(cwl_type), user_types)

        return basic_example_value(name, cwl_type)
