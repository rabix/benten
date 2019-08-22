#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, Intelligence, MapSubjectPredicate, TypeCheck, Match
from ..langserver.lspobjects import Range
from ..code.intelligence import IntelligenceContext
from .typeinference import infer_type
from .lib import get_range_for_value


class CWLArrayType(CWLBaseType):

    def __init__(self, name, allowed_types):
        super().__init__(name)
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if isinstance(node, list):
            return TypeCheck(self)
        else:
            return TypeCheck(self, match=Match.No)

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

        for n, v in enumerate(node):
            inferred_type = infer_type(v, self.types)
            inferred_type.parse(
                doc_uri=doc_uri,
                node=v,
                intel_context=intel_context,
                code_intel=code_intel,
                problems=problems,
                value_range=get_range_for_value(node, n),
                requirements=requirements)
