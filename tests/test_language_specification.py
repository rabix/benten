#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from benten.cwl.specification import parse_schema


current_path = pathlib.Path(__file__).parent
schema_fname = pathlib.Path(current_path, "../benten/000.package.data/schema-v1.0.json")


def test_load_language_specification():

    lang_model = parse_schema(schema_fname)

    assert "Array_symbol" in lang_model
    assert "CommandLineTool" in lang_model
    assert "Workflow" in lang_model
    assert "steps" in lang_model["Workflow"].fields
    assert lang_model["Workflow"].fields["steps"].required
