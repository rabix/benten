import textwrap

from ..langserver.lspobjects import (
    Diagnostic, DiagnosticSeverity, Range, Position, DocumentSymbol, SymbolKind)
from .base import Base

import logging
logger = logging.getLogger(__name__)


def truncate(text):
    if isinstance(text, str):
        if len(text):
            return textwrap.shorten(text, 20, placeholder="...")
    return "-"


CWLSymbol = {
    "class": {
        "kind": SymbolKind.Constant,
        "name": lambda k, v: v
    },
    "cwlVersion": {
        "kind": SymbolKind.Constant,
        "name": lambda k, v: v
    },
    "id": {
        "kind": SymbolKind.Field,
        "name": lambda k, v: truncate(v)
    },
    "label": {
        "kind": SymbolKind.Field,
        "name": lambda k, v: truncate(v)
    },
    "inputs": {
        "kind": SymbolKind.Interface,
        "name": lambda k, v: "-"
    },
    "outputs": {
        "kind": SymbolKind.Interface,
        "name": lambda k, v: "-"
    },
    "expression": {
        "kind": SymbolKind.Function,
        "name": lambda k, v: "{}"
    },
    "requirements": {
        "kind": SymbolKind.Array,
        "name": lambda k, v: "-"
    },
    "hints": {
        "kind": SymbolKind.Array,
        "name": lambda k, v: "-"
    },
    "steps": {
        "kind": SymbolKind.Class,
        "name": lambda k, v: "-"
    }
}

CWLSymbolDefault = {
        "kind": SymbolKind.Field,
        "name": lambda k, v: k
}


class Process(Base):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outline_info = {}

    def parse_sections(self, fields):
        for k, v in self.ydict.items():
            self.outline_info[k] = {
                "kind": CWLSymbol.get(k, CWLSymbolDefault)["kind"],
                "name": CWLSymbol.get(k, CWLSymbolDefault)["name"](k, v),
                "range": (v.start, v.end)
            }

        for k in self.outline_info.keys():
            if k not in fields:
                self.problems += [
                    Diagnostic(
                        _range=Range(
                            start=Position(self.ydict[k].start.line, 0),
                            end=Position(self.ydict[k].end.line, self.ydict[k].end.column)),
                        message=f"Illegal section: {k}",
                        severity=DiagnosticSeverity.Error,
                        code="CWL err",
                        source="Benten")]

        for k, _required in fields.items():
            if _required:
                if k not in self.outline_info:
                    self.problems += [
                        Diagnostic(
                            _range=Range(start=Position(0, 0), end=Position(0, 1)),
                            message=f"Missing required section: {k}",
                            severity=DiagnosticSeverity.Error,
                            code="CWL err",
                            source="Benten")]

    def symbols(self):
        return [
            DocumentSymbol(
                name=v["name"],
                detail=k,
                kind=v["kind"],
                _range=Range(
                    start=Position(v["range"][0].line, v["range"][0].column),
                    end=Position(v["range"][1].line, v["range"][1].column)
                ),
                selection_range=Range(
                    start=Position(v["range"][0].line, v["range"][0].column),
                    end=Position(v["range"][1].line, v["range"][1].column)
                )
            )
            for k, v in self.outline_info.items()
        ]
