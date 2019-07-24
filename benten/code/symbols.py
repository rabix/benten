"""Iterates over the CWL and extracts top level and step symbols"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

import textwrap

from ..langserver.lspobjects import SymbolKind, DocumentSymbol, Position, Range


def truncate(text):
    if isinstance(text, str):
        if len(text):
            return textwrap.shorten(text, 20, placeholder="...")
    return "-"


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


def SymbolDefault(k, v):
    return {
        "kind": SymbolKind.Field,
        "name": k
    }


def extract_symbols(cwl, line_count):
    starts = [cwl.lc.key(k)[0] for k in cwl.keys()]
    starts += [line_count - 1]
    return {
        k: DocumentSymbol(
                _range=Range(
                    start=Position(starts[n], 0),
                    end=Position(starts[n + 1] - 1, 0)
                ),
                selection_range=Range(
                    start=Position(starts[n], 0),
                    end=Position(starts[n + 1] - 1, 0)
                ),
                **Symbols.get(k, SymbolDefault)(k, cwl[k])
            )
        for n, k in enumerate(cwl.keys())
    }


def extract_step_symbols(cwl, symbols):
    _steps = cwl.get("steps")
    if not isinstance(_steps, (list, dict)):
        return symbols

    symb_steps = symbols.get("steps")
    last_line = symb_steps.range.end.line

    if isinstance(_steps, list):
        lines = [_steps.lc.item(n)[0] for n in range(len(_steps))]
        names = []
        for n, v in enumerate(_steps):
            mid = f"Step {n} is missing id!"
            if isinstance(v, dict):
                name = v.get("id", mid)
            else:
                name = mid
            names += [name]
    else:
        lines = [_steps.lc.key(k)[0] for k in _steps.keys()]
        names = [k for k in _steps.keys()]

    lines += [last_line]

    symb_steps.children = [
        DocumentSymbol(
            name=names[n],
            kind=SymbolKind.Field,
            _range=Range(
                start=Position(lines[n], 0),
                end=Position(lines[n+1] - 1, 0)
            ),
            selection_range=Range(
                start=Position(lines[n], 0),
                end=Position(lines[n+1] - 1, 0)
            )
        )
        for n in range(len(names))
    ]

    return symbols
