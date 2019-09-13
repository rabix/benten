#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from benten.code.document import Document


def load(doc_path: pathlib.Path, type_dicts: dict):
    return Document(
        doc_uri=doc_path.as_uri(),
        scratch_path="./",
        text=doc_path.read_text(),
        version=1,
        type_dicts=type_dicts)