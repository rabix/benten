"""
textDocument/documentSymbol
"""

from .base import CWLLangServerBase

import logging
logger = logging.getLogger(__name__)


class DocumentSymbol(CWLLangServerBase):

    def serve_textDocument_documentSymbol(self, client_query):
        params = client_query["params"]
        doc_uri = params["textDocument"]["uri"]

        doc = self.open_documents[doc_uri]
        logger.debug(type(doc.model))
        return doc.model.symbols()
