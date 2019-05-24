"""
textDocument/documentSymbol
"""
#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
import json
import hashlib

from .base import CWLLangServerBase

import logging
logger = logging.getLogger(__name__)


class DocumentSymbol(CWLLangServerBase):

    def serve_textDocument_documentSymbol(self, client_query):
        params = client_query["params"]
        doc_uri = params["textDocument"]["uri"]

        doc = self.open_documents[doc_uri]
        logger.debug(type(doc.model))

        self._write_out_graph(doc)
        return doc.model.symbols()

    def _write_out_graph(self, doc):
        graph_data_file = pathlib.Path(
            self.config.scratch_path,
            hashlib.md5(doc.doc_uri.encode()).hexdigest() + ".json")
        with graph_data_file.open("w") as f:
            json.dump(doc.model.graph(), f, indent=2)
