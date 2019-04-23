"""
textDocument/completion
"""

from .lspobjects import Position
from .base import CWLLangServerBase

import logging
logger = logging.getLogger(__name__)


class Completion(CWLLangServerBase):

    def serve_textDocument_completion(self, client_query):
        params = client_query["params"]
        doc_uri = params["textDocument"]["uri"]
        position = Position(**params["position"])

        doc = self.open_documents[doc_uri]
        compl = doc.model.completions(position, self.config.snippets)
        logger.debug(len(compl.items))
        return compl

