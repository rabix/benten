#  Copyright (c) 2019-2020 Seven Bridges. See LICENSE

import pathlib
import json

from benten.cwl.specification import parse_schema
from benten.cwl.basetype import CWLBaseType


current_path = pathlib.Path(__file__).parent
schema_fname = pathlib.Path(current_path, "../benten_schemas/schema-v1.0.json")


def test_load_language_specification():

    with open(schema_fname) as f:
        lang_model = parse_schema(json.load(f))

    assert isinstance(lang_model.get("null"), CWLBaseType)
    assert "Array_symbol" in lang_model
    assert "CommandLineTool" in lang_model
    assert "Workflow" in lang_model
    assert "steps" in lang_model["Workflow"].fields
    assert lang_model["Workflow"].fields["steps"].required

    # Ensure type is properly initialized after forward construction
    assert "entry" in lang_model["Dirent"].required_fields


def test_forward_reference_resolution():
    with open(schema_fname) as f:
        type_dict = parse_schema(json.load(f))
    for _, _type in type_dict.items():
        check_for_unresolved_references(_type, type_dict, set())


def check_for_unresolved_references(_type, type_dict, parents):
    assert not isinstance(_type, str)

    if _type in parents:
        return
    else:
        parents.add(_type)

    if hasattr(_type, "types"):
        for _t in _type.types:
            check_for_unresolved_references(_t, type_dict, parents)

    if hasattr(_type, "fields"):
        for _, field in _type.fields.items():
            check_for_unresolved_references(field, type_dict, parents)
