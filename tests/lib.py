#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from benten.code.document import Document

from benten.cwl.specification import parse_schema


def load(doc_path: pathlib.Path, type_dicts: dict):
    return Document(
        doc_uri=doc_path.as_uri(),
        scratch_path="./",
        text=doc_path.read_text(),
        version=1,
        type_dicts=type_dicts)


current_path = pathlib.Path(__file__).parent
schema_path = pathlib.Path(current_path, "../benten/000.package.data/")


def load_type_dicts():
    type_dicts = {}
    for fname in schema_path.glob("schema-*.json"):
        version = fname.name[7:-5]
        type_dicts[version] = parse_schema(fname)
    return type_dicts
