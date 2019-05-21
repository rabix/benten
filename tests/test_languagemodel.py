#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from benten.models.languagemodel import load_languagemodel


current_path = pathlib.Path(__file__).parent


def test_load_languagemodel():

    fname = pathlib.Path(current_path, "../benten/000.package.data/schema-v1.0.json")
    lang_model = load_languagemodel(fname)

    assert "CommandLineTool" in lang_model
    assert "Workflow" in lang_model
    assert "steps" in lang_model["Workflow"].fields
    assert lang_model["Workflow"].fields["steps"].required
