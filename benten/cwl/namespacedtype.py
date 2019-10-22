#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, MapSubjectPredicate, TypeCheck
from ..code.intelligence import Intelligence
from ..code.intelligencecontext import IntelligenceContext
from ..langserver.lspobjects import Range, Diagnostic, DiagnosticSeverity

import logging
logger = logging.getLogger(__name__)


class CWLNameSpacedType(CWLBaseType):

    def __init__(self, name):
        super().__init__(name)

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

        _s = self.name.split(":")
        if _s[0] not in code_intel.namespaces:
            problems += [
                Diagnostic(
                    _range=key_range or value_range,
                    message=f"Expecting one of: {sorted(code_intel.namespaces)}",
                    severity=DiagnosticSeverity.Error)
            ]
