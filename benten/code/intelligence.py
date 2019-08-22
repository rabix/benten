"""Provides classes that can be used to infer document location
from cursor location and provide auto-completions.

Language Model objects parse the document to produce document
model objects.

For details see ../../docs/document-model.md
"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from typing import List

from ..langserver.lspobjects import (Position, Range, CompletionItem)


import logging
logger = logging.getLogger(__name__)


class LookupNode:

    def __init__(self, loc: Range):
        self.loc = loc
        self.intelligence_node = None


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

    def add_lookup_node(self, node: LookupNode):
        self.lookup_table.append(node)

    def get_doc_element(self, loc: Position):
        # O(n) algorithm, but should do fine for our file sizes
        # For now doing exact matches on lines, which is sufficient
        for n in self.lookup_table:
            if n.loc.start.line == loc.line:
                if n.loc.start.character <= loc.character <= n.loc.end.character:
                    return n.intelligence_node

        return None
