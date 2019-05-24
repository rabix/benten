"""
textDocument/definition
"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .lspobjects import Position
from .base import CWLLangServerBase

import logging
logger = logging.getLogger(__name__)


class Definition(CWLLangServerBase):

    def serve_textDocument_definition(self, client_query):
        params = client_query["params"]
        doc_uri = params["textDocument"]["uri"]
        position = Position(**params["position"])

        doc = self.open_documents[doc_uri]
        return doc.model.definition(position)

