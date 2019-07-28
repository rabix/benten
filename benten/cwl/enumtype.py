#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, IntelligenceContext, Intelligence, MapSubjectPredicate, TypeCheck, Match
from ..langserver.lspobjects import Range, CompletionItem, Diagnostic, DiagnosticSeverity
from ..code.intelligence import LookupNode

import logging
logger = logging.getLogger(__name__)


class CWLEnumType(CWLBaseType):

    def __init__(self, name: str, symbols: set):
        super().__init__(name)
        self.symbols = symbols

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:

        if not (isinstance(node, str) or None):
            return TypeCheck(
                cwl_type=self,
                match=Match.No)
        else:
            return TypeCheck(cwl_type=self)

    def parse(self,
              doc_uri: str,
              node,
              intel_context: IntelligenceContext,
              code_intel: Intelligence,
              problems: list,
              node_key: str = None,
              map_sp: MapSubjectPredicate = None,
              key_range: Range = None,
              value_range: Range = None,
              requirements=None):

        symbols = self.symbols
        if self.name in ["PrimitiveType", "CWLType"]:
            # Special treatment for syntactic sugar around types
            symbols = [
                sy + ext for sy in self.symbols for ext in ["", "[]", "?", "[]?"]
            ]

        if node not in symbols:

            problems += [
                Diagnostic(
                    _range=value_range,
                    message=f"Expecting one of: {self.symbols}",
                    severity=DiagnosticSeverity.Error)
            ]

        ln = LookupNode(loc=value_range)
        ln.intelligence_node = self
        code_intel.add_lookup_node(ln)

    def completion(self):
        return [CompletionItem(label=s) for s in self.symbols]
