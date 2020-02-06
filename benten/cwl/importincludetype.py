"""Represents an $include or $import"""

#  Copyright (c) 2020 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, IntelligenceContext, Intelligence, MapSubjectPredicate
from .linkedfiletype import CWLLinkedFile
from .linkedschemadeftype import CWLLinkedSchemaDef
from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity, Range
from .lib import get_range_for_key, get_range_for_value


class CWLImportInclude(CWLBaseType):

    def __init__(self, key, import_context):
        super().__init__("Import/Include")
        self.key = key
        self.import_context = import_context

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

        if len(node) > 1:
            problems += [
                Diagnostic(
                    _range=value_range,
                    message=f"{self.key} has to be the only key",
                    severity=DiagnosticSeverity.Error)
            ]
            return

        if self.import_context == "InputRecordSchema":
            if self.key != "$import":
                problems += [
                    Diagnostic(
                        _range=value_range,
                        message=f"Expecting an $import",
                        severity=DiagnosticSeverity.Error)
                ]
                return
            inferred_type = CWLLinkedSchemaDef(prefix=node.get("$import"))
        else:
            inferred_type = CWLLinkedFile(prefix=node.get(self.key))

        inferred_type.parse(
            doc_uri=doc_uri,
            node=node.get(self.key),
            intel_context=intel_context,
            code_intel=code_intel,
            problems=problems,
            node_key=self.key,
            map_sp=map_sp,
            key_range=key_range,
            value_range=get_range_for_value(node, self.key),
            requirements=requirements)
