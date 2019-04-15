"""

"""
import pathlib

from .lspobjects import Position
from .base import CWLLangServerBase
from ..models.document import Document
from ..models.lineloader import compute_path
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
            if len(doc.yaml_error) == 0:
                p = compute_path(
                    doc=doc.yaml,
                    line=position.line,
                    column=position.character
                )
                logger.debug(p)

        return {}
