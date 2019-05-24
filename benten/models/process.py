#  Copyright (c) 2019 Seven Bridges. See LICENSE

import textwrap
import pathlib
import urllib.parse
import time

from .lineloader import compute_path, lookup
from .languagemodel import select_language_model, infer_model_from_type
from ..langserver.lspobjects import (
    Diagnostic, DiagnosticSeverity, Range, Position, Location, DocumentSymbol, SymbolKind)
from .base import Base

import logging
logger = logging.getLogger(__name__)


def truncate(text):
    if isinstance(text, str):
        if len(text):
            return textwrap.shorten(text, 20, placeholder="...")
    return "-"


def resolve_file_path(doc_uri, target_path):
    _path = pathlib.PurePosixPath(target_path)
    if not _path.is_absolute():
        base_path = pathlib.Path(urllib.parse.urlparse(doc_uri).path).parent
    else:
        base_path = "."
    _path = pathlib.Path(base_path / _path).resolve().absolute()
    logger.debug(f"Resolved URI: {_path.as_uri()}")
    return _path


class Process(Base):

    # SymbolKind has a nice representation in the VS Code UI
    Symbols = {
        "class": lambda k, v: {
            "kind": SymbolKind.File,
            "name": k,
            "detail": v
        },
        "cwlVersion": lambda k, v: {
            "kind": SymbolKind.Constant,
            "name": k,
            "detail": v
        },
        "id": lambda k, v: {
            "kind": SymbolKind.String,
            "name": truncate(v)
        },
        "label": lambda k, v: {
            "kind": SymbolKind.String,
            "name": truncate(v)
        },
        "doc": lambda k, v: {
            "kind": SymbolKind.String,
            "name": truncate(v)
        },
        "inputs": lambda k, v: {
            "kind": SymbolKind.Interface,
            "name": k
        },
        "outputs": lambda k, v: {
            "kind": SymbolKind.Interface,
            "name": k
        },
        "baseCommand": lambda k, v: {
            "kind": SymbolKind.Operator,
            "name": k
        },
        "expression": lambda k, v: {
            "kind": SymbolKind.Function,
            "name": "{}"
        },
        "requirements": lambda k, v: {
            "kind": SymbolKind.Array,
            "name": k
        },
        "hints": lambda k, v: {
            "kind": SymbolKind.Array,
            "name": k
        },
        "steps": lambda k, v: {
            "kind": SymbolKind.Class,
            "name": k
        }
    }

    @staticmethod
    def SymbolDefault(k, v):
        return {
            "kind": SymbolKind.Field,
            "name": k
        }

    def _create_document_symbol(self, k, v):
        _start_pos = Position(v.start.line, v.start.column)
        _end_pos = Position(v.end.line, v.end.column)
        return DocumentSymbol(
            _range=Range(
                start=_start_pos,
                end=_end_pos
            ),
            selection_range=Range(
                start=_start_pos,
                end=_end_pos
            ),
            **self.Symbols.get(k, self.SymbolDefault)(k, v)
        )

    def __init__(self, *args, **kwargs):
        self._symbols = {}
        super().__init__(*args, **kwargs)
        self._run_validations()
        self._symbols = {k: self._create_document_symbol(k, v) for k, v in self.ydict.items()}

    def definition(self, position: Position):
        p = self._compute_path(position)
        return self._definition(p)

    def hover(self, position: Position, base_uri: str):
        return None
        # return {
        #     "contents": {
        #         "kind": "markdown",
        #         "value": str(self._compute_path(position))
        #     },
        #     "range": Range(
        #         start=position, end=Position(position.line, position.character + 100))
        # }

    def symbols(self):
        return list(self._symbols.values())

    def _compute_path(self, position: Position):
        p = compute_path(
            doc=self.ydict,
            line=position.line,
            column=position.character
        )
        logger.debug(f"Path at cursor: {p}")
        return p

    def _lookup(self, path):
        return lookup(self.ydict, path)

    # def _resolve_file_path(self, uri):
    #     _path = pathlib.Path(urllib.parse.urlparse(uri).path)
    #     if not _path.is_absolute():
    #         base_path = pathlib.Path(urllib.parse.urlparse(self.doc_uri).path)
    #         _path = pathlib.Path(base_path.parent, _path).absolute()
    #     logger.debug(f"Resolved URI: {_path.as_uri()}")
    #     return _path

    def _definition(self, p):
        if len(p) and p[-1] == "$import":
            uri = self._lookup(p)
            if isinstance(uri, str):
                return Location(resolve_file_path(self.doc_uri, uri).as_uri())

    def _run_validations(self):

        t0 = time.time()
        lang_model = infer_model_from_type(
            self.ydict,
            select_language_model(self.ydict, self.language_models))
        lang_model.validate(self.ydict, self.problems)
        logger.info(f"Validated document in {time.time() - t0}s")

        if not self._validate_inline_js():
            self.problems += [
                Diagnostic(
                    _range=Range(start=Position(0, 0), end=Position(0, 1)),
                    message="Javascript detected but missing InlineJavascriptRequirement",
                    severity=DiagnosticSeverity.Error,
                    code="CWL err",
                    source="Benten")]

    def _validate_inline_js(self):
        if self.ydict.contains(patterns=("${",), in_fields=("valueFrom", "outputEval")):
            req = self.ydict.get("requirements")
            if req is not None:
                return "InlineJavascriptRequirement" in req
            else:
                return False
        else:
            return True
