"""
Generate inputs, outputs for processes, including intermediate outputs for workflows

The sample data is stored in a dictionary with the following structure

{
    "inputs":
        "in1": ...,
        "step1/out1": ...
    "outputs":
        "out1": ...,
        "out2": ...
}
"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

import random
import string

from ..cwl.lib import resolve_file_path, list_as_map
from .schemadef import extract_schemadef
from .yaml import fast_load


def get_sample_runtime(cwl: dict, doc_path: tuple):
    runtime = {
        "outdir": "/out/dir",
        "tmpdir": "/tmp/dir",
        "cores": 4,
        "ram": 1024,
        "outdirSize": 2048,
        "tmpdirSize": 4096
    }

    # https://www.commonwl.org/v1.1/CommandLineTool.html#Execution
    if "outputEval" in doc_path:
        try:
            if float(cwl.get("cwlVersion")[1:]) > 1.0:
                runtime["exitCode"] = 1
        except ValueError as e:
            pass

    return runtime


def get_sample_data(doc_uri: str, cwl: dict, user_types: dict):
    return {
        "inputs": {
            **generate_sample_inputs(cwl, user_types),
            **generate_sample_intermediate_results(doc_uri, cwl, user_types)
        },
        "outputs": generate_sample_outputs(cwl, user_types)
    }


def get_sample_globbed_files(name):
    return [
        basic_example_value(name + "/globbed_file_" + str(i), "File")
        for i in range(random.randint(0, 4))
    ]


def generate_sample_inputs(cwl: dict, user_types: dict):
    return generate_values(cwl.get("inputs"), user_types)


def generate_sample_outputs(cwl: dict, user_types: dict):
    return generate_values(cwl.get("outputs"), user_types)


def generate_sample_intermediate_results(doc_uri: str, cwl: dict, parent_user_types):
    return {
        step_id + "/" + k: v
        for step_id, step in list_as_map(cwl.get("steps"), key_field="id", problems=[]).items()
        for k, v in extract_step_sample_outputs(doc_uri, step.get("run"), parent_user_types).items()
    }


def generate_values(_ports: dict, user_types: dict):
    if not isinstance(_ports, (list, dict)):
        _ports = {}
    return {
        k: example_value(k, _type_v, user_types)
        for k, _type_v in list_as_map(_ports, key_field="id", problems=[]).items()
    }


# This should be invoked when we arrive at the "run" field of a workflow
def extract_step_sample_outputs(doc_uri: str, run_field, parent_user_types):

    # todo: verify this works with inlined steps
    user_types = parent_user_types
    if isinstance(run_field, str):
        linked_file = resolve_file_path(doc_uri, run_field)
        if linked_file.exists() and linked_file.is_file():
            run_field = fast_load.load(linked_file)
            user_types = extract_schemadef(linked_file.as_uri(), run_field)

    outputs = {}
    if isinstance(run_field, dict):
        outputs = generate_sample_outputs(run_field, user_types)

    return outputs


def basic_example_value(name, _type):
    name = name + "_" + "".join(random.choices(string.ascii_letters, k=5))
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
        return file_example_value(name, _type)
    elif _type == 'Directory':
        return {
            'class': 'Directory',
            'path': f'/path/to/{name}'
        }


def file_example_value(name, cwl_type, ext=".ext"):
    ex_file = _example_file(name, ext)
    if isinstance(cwl_type, dict) and "secondaryFiles" in cwl_type:
        ex_file["secondaryFiles"] = [
            _example_file(name, sec_ext)
            for sec_ext in cwl_type.get("secondaryFiles")
        ]
    return ex_file


def _example_file(name, ext):
    fsize = random.randint(0, 100)
    contents = "".join(random.choices(string.ascii_letters, k=fsize))
    return {
        'class': 'File',
        'path': f'/path/to/{name}.ext',
        'location': f'/location/of/{name}.ext',
        'basename': f'{name}.ext',
        'dirname': '/path/to/',
        'nameroot': name,
        'nameext': '.ext',
        'checksum': "sha1$deadbeef",
        'size': fsize,
        'format': 'someformat',
        'contents': contents
    }


def enum_example_value(symbols):
    return symbols[random.randint(0, len(symbols) - 1)]


def record_example_value(name, _type, user_types):
    return {
        k: example_value(f"{name}/{k}", _type_v, user_types)
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
        elif _type == "File":
            return file_example_value(name, cwl_type)
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
