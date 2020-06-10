#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, IntelligenceContext, Intelligence, MapSubjectPredicate, TypeCheck, Match
from ..langserver.lspobjects import Range, CompletionItem, Diagnostic, DiagnosticSeverity, Hover
from ..code.intelligence import LookupNode
from ..code.yaml import yaml_to_string
from .lib import normalized_path

import logging
logger = logging.getLogger(__name__)


class CWLEnumType(CWLBaseType):

    def __init__(self, name: str, symbols: set):
        super().__init__(name)
        self.symbols = symbols
        self._hover_value = None

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:

        if not (isinstance(node, str) or None):
            return TypeCheck(
                cwl_type=self,
                match=Match.No)
        else:
            if self.name in ["PrimitiveType", "CWLType"]:
                # Special treatment for data types
                return TypeCheck(cwl_type=CWLDataType(node, self.symbols))
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

        if node not in self.symbols:
            problems += [
                Diagnostic(
                    _range=value_range,
                    message=f"Expecting one of: {sorted(self.symbols)}",
                    severity=DiagnosticSeverity.Error)
            ]

        ln = LookupNode(loc=value_range)
        ln.intelligence_node = self
        code_intel.add_lookup_node(ln)

    def completion(self):
        return [CompletionItem(label=s) for s in self.symbols]


class CWLDataType(CWLEnumType):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_types = []
        self.prefix = ""

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

        self.prefix = node
        self.user_types = code_intel.type_defs.keys()

        # de-sugar
        if node[-1] == "?":
            node = node[:-1]
        if node[-2:] == "[]":
            node = node[:-2]

        if node not in self.symbols: # Not a native type
            if node not in code_intel.type_defs: # Path doesn't match denormalized
                _norm_path = normalized_path(doc_uri, node)
                for _type in code_intel.type_defs.keys():
                    if _norm_path == normalized_path(doc_uri, _type):
                        break
                else:
                    problems += [
                        Diagnostic(
                            _range=value_range,
                            message=f"Expecting one of: {sorted(set(self.symbols).union(code_intel.type_defs.keys()))}",
                            severity=DiagnosticSeverity.Error)
                    ]

            else:
                self._hover_value = code_intel.type_defs[node]

        ln = LookupNode(loc=value_range)
        ln.intelligence_node = self
        code_intel.add_lookup_node(ln)

    def hover(self):
        if self._hover_value is not None:
            return Hover(yaml_to_string(self._hover_value), hover_type=Hover.HoverType.Code)

    def completion(self):
        return [CompletionItem(label=s) for s in self.symbols.union(self.user_types)]
