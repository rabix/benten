"""
textDocument/definition
"""
import os
import pathlib
import urllib
import urllib.parse

from .lspobjects import Position, Location
from .base import CWLLangServerBase
from ..models.lineloader import compute_path, lookup
from ..models.workflow import Workflow

import logging
logger = logging.getLogger(__name__)


class Definition(CWLLangServerBase):

    def serve_textDocument_definition(self, client_query):
        params = client_query["params"]
        doc_uri = params["textDocument"]["uri"]
        position = Position(**params["position"])

        doc = self.open_documents[doc_uri]
        if isinstance(doc.model, Workflow):
            p = compute_path(
                doc=doc.model.ydict,
                line=position.line,
                column=position.character
            )
            logger.debug(f"Path at cursor: {p}")
            if p[-1] == "run" and p[-3] == "steps":
                step_uri = lookup(doc.model.ydict, p)
                if isinstance(step_uri, str):
                    logger.debug(f"Doc URI: {doc_uri}, Step URI: {step_uri}")
                    step_path = pathlib.Path(urllib.parse.urlparse(step_uri).path)
                    if not step_path.is_absolute():
                        doc_path = pathlib.Path(urllib.parse.urlparse(doc_uri).path)
                        step_path = pathlib.Path(doc_path.parent, step_path).absolute()
                    return Location(step_path.as_uri())

        return {}
