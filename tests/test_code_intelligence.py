#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from benten.code.document import Document
from benten.cwl.specification import parse_schema
from benten.langserver.lspobjects import Position, Location


current_path = pathlib.Path(__file__).parent
schema_path = pathlib.Path(current_path, "../benten/000.package.data/")


def load(doc_path: pathlib.Path, type_dicts: dict):
    return Document(
        doc_uri=doc_path.as_uri(),
        text=doc_path.read_text(),
        version=1,
        type_dicts=type_dicts)


def load_type_dicts():
    type_dicts = {}
    for fname in schema_path.glob("schema-*.json"):
        version = fname.name[7:-5]
        type_dicts[version] = parse_schema(fname)
    return type_dicts


type_dicts=load_type_dicts()
path = current_path / "cwl" / "ebi" / "workflows" / "cmsearch-multimodel-wf.cwl"


def test_definition():
    doc = load(doc_path=path, type_dicts=type_dicts)
    linked_uri = pathlib.Path(current_path / "cwl" / "ebi" / "utils" / "concatenate.cwl")
    doc_def_loc = doc.definition(loc=Position(50, 20))
    assert isinstance(doc_def_loc, Location)
    assert doc_def_loc.uri == linked_uri.as_uri()


def test_record_field_completion():
    doc = load(doc_path=path, type_dicts=type_dicts)
    cmpl = doc.completion(Position(7, 0))
    assert "doc" in [c.label for c in cmpl]


def test_type_completion():
    doc = load(doc_path=path, type_dicts=type_dicts)
    cmpl = doc.completion(Position(14, 11))
    assert "string" in [c.label for c in cmpl]


def test_step_input_completion():
    doc = load(doc_path=path, type_dicts=type_dicts)
    cmpl = doc.completion(Position(37, 38))
    assert "covariance_models" in [c.label for c in cmpl]


def test_requirement_completion():
    doc = load(doc_path=path, type_dicts=type_dicts)
    cmpl = doc.completion(Position(8, 16))
    assert "InlineJavascriptRequirement" in [c.label for c in cmpl]
