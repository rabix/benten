#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, Workflow, Intelligence, MapSubjectPredicate, TypeCheck, Match
from ..langserver.lspobjects import Range, CompletionItem, Diagnostic, DiagnosticSeverity
from ..code.intelligence import LookupNode, IntelligenceContext

import logging
logger = logging.getLogger(__name__)


class CWLRequirementsType(CWLBaseType):

    def __init__(self, name, req_types):
        super().__init__(name)
        self.req_types = req_types

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

    def completion(self):
        return [CompletionItem(label=k.name) for k in self.req_types]
