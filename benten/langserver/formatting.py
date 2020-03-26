"""
textDocument/formatting
"""

#  Copyright (c) 2020 Seven Bridges. See LICENSE

from cwlformat.formatter import cwl_format

from .base import CWLLangServerBase
from .lspobjects import Position, Range, TextEdit

import logging
logger = logging.getLogger(__name__)


class Formatting(CWLLangServerBase):

    def serve_textDocument_formatting(self, client_query):
        params = client_query["params"]
        doc_uri = params["textDocument"]["uri"]
        doc = self.open_documents[doc_uri]

        if len(doc.text) == 0:
            return

        lines = doc.text.splitlines()
        _start = Position(0, 0)
        _end = Position(len(lines), len(lines[-1]))
        return [TextEdit(_range=Range(start=_start, end=_end), new_text=cwl_format(doc.text))]
