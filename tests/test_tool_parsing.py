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


def test_mass_load():
    type_dicts = load_type_dicts()
    for wf_dir in ["ebi/tools", "mgi/tools"]:
        path = current_path / "cwl" / wf_dir
        for fname in path.glob("*.cwl"):
            doc = load(doc_path=fname, type_dicts=type_dicts)
