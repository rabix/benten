#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import (CWLBaseType, MapSubjectPredicate, TypeCheck, Match,
                       Intelligence, IntelligenceContext)
from ..langserver.lspobjects import Range, Hover
from ..code.intelligence import LookupNode

import logging
logger = logging.getLogger(__name__)


class CWLExpressionType(CWLBaseType):

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if isinstance(node, str):
            if "$(" in node or "${" in node:
                return TypeCheck(cwl_type=CWLExpression(node))

        return TypeCheck(cwl_type=self, match=Match.No)


class CWLExpression(CWLBaseType):

    def __init__(self, expression: str):
        super().__init__("Expression")
        self.expression = expression

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if isinstance(node, str):
            if "$(" in node or "${" in node:
                return TypeCheck(cwl_type=self)

        return TypeCheck(cwl_type=self, match=Match.No)

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

        ln = LookupNode(loc=value_range)
        ln.intelligence_node = self
        code_intel.add_lookup_node(ln)

    # Future expansion: expression evaluation on hover
    def hover(self):
        return Hover(f"Evaluate {self.expression}")

