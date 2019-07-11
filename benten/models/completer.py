"""Provides classes that can be used to infer document location
from cursor location and provide auto-completions.

Language Model objects parse the document to produce document
model objects.

For details see ../../docs/document-model.md
"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from enum import IntEnum
from typing import Union, List, Dict

from ..langserver.lspobjects import (Position, Range, CompletionItem)


import logging
logger = logging.getLogger(__name__)


class Style(IntEnum):
    block = 1
    flow = 2
    none = 3


class CompleterNode:

    def __init__(self,
                 indent: int,
                 style: Style,
                 completions: List[str],
                 parent: Union[None, 'CompleterNode']):
        self.indent = indent
        self.style = style
        self._completions = completions

        self.parent = parent

        self.custom_completer = None

    def completions(self, prefix):
        if self.custom_completer is not None:
            return self.custom_completer(prefix)
        else:
            return [CompletionItem(label=c) for c in self._completions]


class LookupNode:

    def __init__(self, loc: Range):
        self.loc = loc
        self.completer_node = None


class KeyLookup(LookupNode):

    @classmethod
    def from_key(cls, parent, key):
        start = parent.lc.key(key)
        end = (start[0], start[1] + len(key))
        return cls(Range(Position(*start), Position(*end)))


class ValueLookup(LookupNode):

    @classmethod
    def from_value(cls, parent, key):
        if isinstance(parent, dict):
            start = parent.lc.value(key)
        else:
            start = parent.lc.item(key)

        v = parent[key]
        if v is None:
            v = ""
        else:
            v = str(v)  # How to handle multi line strings

        end = (start[0], start[1] + len(v))
        return cls(Range(Position(*start), Position(*end)))


class Completer:

    def __init__(self):
        self.lookup_table: List[LookupNode] = []
        self.nodes: List[CompleterNode] = []

    def add_lookup_node(self, node: LookupNode):
        self.lookup_table.append(node)

    def add_completer_node(self, node: CompleterNode):
        self.nodes.append(node)
