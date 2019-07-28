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


class LookupNode:

    def __init__(self, loc: Range):
        self.loc = loc
        self.intelligence_node = None


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


class IntelligenceNode:

    def __init__(self, completions: List[str]=None):
        self._completions = completions

    def completion(self):
        return [CompletionItem(label=c) for c in self._completions]

    def hover(self):
        pass

    def definition(self):
        pass


# Children of maps need to track their ancestors for completions
class IntelligenceContext:
    pass


class Intelligence:

    def __init__(self):
        self.lookup_table: List[LookupNode] = []
        self.nodes: List[IntelligenceNode] = []

        self.wf_completer = None
        # TODO: Refactor these in a more principled manner

    def add_lookup_node(self, node: LookupNode):
        self.lookup_table.append(node)

    def add_intelligence_node(self, node: IntelligenceNode):
        self.nodes.append(node)

    def get_doc_element(self, loc: Position):
        # O(n) algorithm, but should do fine for our file sizes
        # For now doing exact matches on lines, which is sufficient
        for n in self.lookup_table:
            if n.loc.start.line == loc.line:
                if n.loc.start.character <= loc.character <= n.loc.end.character:
                    return n.intelligence_node

        return None
