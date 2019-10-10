#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from benten.cwl.specification import parse_schema
from benten.langserver.lspobjects import Position

from lib import load, load_type_dicts

current_path = pathlib.Path(__file__).parent
schema_path = pathlib.Path(current_path, "../benten/000.package.data/")

type_dicts=load_type_dicts()


def test_basic_JS():
    path = current_path / "cwl" / "misc" / "clt1.cwl"
    doc = load(doc_path=path, type_dicts=type_dicts)

    hov = doc.hover(loc=Position(7, 25))
    assert isinstance(hov.contents, str)
    assert hov.contents.startswith("A_")

    hov = doc.hover(loc=Position(10, 19))
    assert isinstance(hov.contents, str)
    assert "outdirSize" in hov.contents


# Todo: test #custom mechanism


def test_v1_1_runtime():

    # No exitcode in runtime in v1.0 ever
    path = current_path / "cwl" / "misc" / "clt1.cwl"
    doc = load(doc_path=path, type_dicts=type_dicts)

    hov = doc.hover(loc=Position(10, 19))
    assert "exitCode" not in hov.contents

    hov = doc.hover(loc=Position(17, 33))
    assert "exitCode" not in hov.contents

    # Exitcode in runtime in v1.1 when in output
    path = current_path / "cwl" / "misc" / "clt2.cwl"
    doc = load(doc_path=path, type_dicts=type_dicts)

    hov = doc.hover(loc=Position(24, 20))
    assert "exitCode" not in hov.contents

    hov = doc.hover(loc=Position(31, 34))
    assert "exitCode" in hov.contents
