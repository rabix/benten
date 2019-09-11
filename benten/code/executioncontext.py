"""Manages aspects related to test executions of the CWL and of JS expressions.

One of the more interesting decisions to be taken is the test input
auto-generation. We'd like the system to automatically create test
inputs based on the input schema, but we'd like the user to be able
to edit the schema to their liking. What happens when the schema
is regenerated? It would be bad UI to overwrite the user's test data
every time, but we need to discard stale inputs and auto=generate
new inputs when the document changes.

We do the following: we generate the test data afresh each time
and we load the test data too. We then delete any keys in the
test data that are absent in the schema, and we write in any
keys that are present in the generated data, but absent in the
existing test data.
"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
import subprocess
import random

from ..cwl.lib import un_mangle_uri, list_as_map

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

fast_load = YAML(typ='safe')

import logging
logger = logging.getLogger(__name__)


job_inputs_ext = ".benten.test.job.yml"


def merge(user, auto):
    if isinstance(user, dict) and isinstance(auto, dict):
        for k in list(user.keys()):
            if k not in auto:
                user.pop(k)

        for k, v in auto.items():
            if k not in user:
                user[k] = v

        for k in user.keys():
            if (isinstance(auto[k], dict) and not isinstance(user[k], dict)) or \
                    (not isinstance(auto[k], dict) and isinstance(user[k], dict)):
                user[k] = auto[k]
            elif isinstance(auto[k], dict) and isinstance(user[k], dict):
                merge(user[k], auto[k])


class ExecutionContext:
    """Carries the job object (sample inputs) and expression lib for this process"""

    def __init__(self):
        self.context_error = None
        self.job_inputs = {}
        self.runtime = {
            "outdir": "/out/dir",
            "tmpdir": "/tmp/dir",
            "cores": 4,
            "ram": 1024,
            "outdirSize": 2048,
            "tmpdirSize": 4096
        }
        self.expression_lib = []

    def set_job_inputs(self, uri: str, cwl: dict, user_types: dict):
        cwl_uri = un_mangle_uri(uri)
        ex_job_file = cwl_uri.with_suffix(job_inputs_ext)
        _inputs = cwl.get("inputs")
        if not isinstance(_inputs, (list, dict)):
            _inputs = {}
        auto_set_inputs = {
            k: example_value(k, _type_v, user_types)
            for k, _type_v in list_as_map(_inputs, key_field="id", problems=[]).items()
        }

        user_set_inputs = {}
        if ex_job_file.exists():
            try:
                user_set_inputs = fast_load.load(ex_job_file.open().read() or "")
                logger.debug(user_set_inputs)
            except (ParserError, ScannerError) as e:
                logger.error(f"Parsing error loading test input file {ex_job_file}")
                user_set_inputs = {}

        merge(user_set_inputs, auto_set_inputs)
        self.job_inputs = user_set_inputs
        logger.debug(self.job_inputs)

    def set_expression_lib(self, expression_lib: list=None):
        self.expression_lib = expression_lib


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
            return example_value(name, _type.get("items"), user_types, array_of=True)
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
