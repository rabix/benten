#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
import tempfile

from benten.code.document import Document
import benten.configuration


def load(doc_path: pathlib.Path, type_dicts: dict):
    return Document(
        doc_uri=doc_path.as_uri(),
        scratch_path=tempfile.mkdtemp(prefix="benten-test"),
        text=doc_path.read_text(),
        version=1,
        type_dicts=type_dicts)


current_path = pathlib.Path(__file__).parent


def load_type_dicts():
    cfg = benten.configuration.Configuration()
    cfg.initialize()
    return cfg.lang_models
