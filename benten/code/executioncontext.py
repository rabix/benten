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
import tempfile

from ..cwl.lib import un_mangle_uri

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

fast_load = YAML(typ='safe')

import logging
logger = logging.getLogger(__name__)


job_inputs_ext = ".benten.test.job.yml"


# def job_inputs_fname(uri):
#     return pathlib.Path(uri + job_inputs_ext)


# def get_job_inputs(uri):
#     jinp = job_inputs_fname(uri)
#
#     _fd, _name = tempfile.mkstemp(suffix=".benten.job.yml")
#
#     auto_set_inputs = subprocess.run(f"cwltool --make-template {_name}", capture_output=True)
#     user_set_inputs = {}
#
#     if jinp.exists():
#         user_set_inputs = fast_load.load(jinp.open().read())
#
#     merge(user_set_inputs, auto_set_inputs)
#
#     return user_set_inputs


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

    def set_job_inputs(self, uri):
        jinp = un_mangle_uri(uri).with_suffix(job_inputs_ext)
        _fd, _name = tempfile.mkstemp(suffix=".benten.job.yml")

        ret = subprocess.run(f"cwltool --make-template {_name}",
                             shell=True, capture_output=True)

        auto_set_inputs = {}
        if ret.returncode:
            self.context_error = f"Unable to create input template: {ret.stderr}"
            logger.error(self.context_error)
        else:
            auto_set_inputs = fast_load.load(_fd.read())

        user_set_inputs = {}
        if jinp.exists():
            try:
                user_set_inputs = fast_load.load(jinp.open().read() or "")
                logger.debug(user_set_inputs)
            except (ParserError, ScannerError) as e:
                logger.error(f"Parsing error loading test input file {jinp}")
                user_set_inputs = {}

        # merge(user_set_inputs, auto_set_inputs)
        self.job_inputs = user_set_inputs
        fast_load.dump(user_set_inputs, jinp)

    def set_expression_lib(self, expression_lib: list=None):
        self.expression_lib = expression_lib


# class ExpressionLib:
#
#     def __init__(self, expression_lib: list=None):
#         self.expression_lib = expression_lib or []
#
#     def eval(self, js_exp: str, input_object: dict):
#         return dukpy.evaljs(self.expression_lib + [js_exp], **input_object)


