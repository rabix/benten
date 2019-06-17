#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
import os
import shutil
import pytest

from benten.models.document import Document
from benten.models.languagemodel import load_languagemodel


current_path = pathlib.Path(__file__).parent
language_models = {
    v: load_languagemodel(pathlib.Path(current_path, f"../benten/000.package.data/schema-{v}.json"))
    for v in ["v1.0"]
}


def test_basic_errors():

    fpath = current_path / pathlib.Path("cwl") / pathlib.Path("workflows") / pathlib.Path("scatter-e1.cwl")

    document = Document(
        doc_uri=fpath.as_uri(),
        text=fpath.open().read(),
        version=1,
        language_models=language_models)

    assert len(document.model.problems) == 4
    assert len([problem for problem in document.model.problems
                if problem.message.startswith("Missing linked file")]) == 1
    assert len([problem for problem in document.model.problems
                if problem.message.startswith("Unknown field")]) == 1
