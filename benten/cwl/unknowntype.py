#  Copyright (c) 2019 Seven Bridges. See LICENSE


from .basetype import CWLBaseType, Workflow, Intelligence, MapSubjectPredicate, TypeCheck, Match
from ..langserver.lspobjects import Range, CompletionItem, Diagnostic, DiagnosticSeverity
from ..code.intelligence import LookupNode

import logging
logger = logging.getLogger(__name__)


class CWLUnknownType(CWLBaseType):

    def __init__(self, name, expected):
        super().__init__(name)
        self.expected = expected

    def parse(self,
              doc_uri: str,
              node,
              enclosing_workflow: Workflow,
              code_intel: Intelligence,
              problems: list,
              node_key: str = None,
              map_sp: MapSubjectPredicate = None,
              key_range: Range = None,
              value_range: Range = None,
              requirements=None):

        problems += [
            Diagnostic(
                _range=value_range,
                message=f"Got type {self.name}. Expecting one of {self.expected}",
                severity=DiagnosticSeverity.Error)
        ]
