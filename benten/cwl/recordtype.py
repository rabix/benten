#  Copyright (c) 2019 Seven Bridges. See LICENSE

from typing import Dict

from .basetype import CWLBaseType, IntelligenceContext, Intelligence, MapSubjectPredicate, TypeCheck, Match
from .linkedfiletype import CWLLinkedFile
from ..langserver.lspobjects import Range, CompletionItem, Diagnostic, DiagnosticSeverity
from ..code.intelligence import LookupNode
from ..code.workflow import Workflow
from .typeinference import infer_type
from .lib import get_range_for_key, get_range_for_value

import logging
logger = logging.getLogger(__name__)


class CWLRecordType(CWLBaseType):

    def __init__(self, name: str, doc: str, fields: Dict[str, 'CWLFieldType']):
        super().__init__(name)
        self.doc = doc
        self.fields = fields
        self.required_fields = set((k for k, v in self.fields.items() if v.required))

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:

        if node is None:
            return TypeCheck(self, Match.No)

        # Exception for $import/$include etc.
        if isinstance(node, dict):
            if "$import" in node:
                return TypeCheck(cwl_type=CWLLinkedFile(node.get("$import")))

        required_fields = self.required_fields - {map_sp.subject if map_sp else None}

        if isinstance(node, str):
            if map_sp is not None and node_key is not None:
                if map_sp.predicate in self.required_fields and len(required_fields) <= 1:
                    return TypeCheck(cwl_type=self)

            return TypeCheck(cwl_type=self, match=Match.No)

        if not isinstance(node, dict):
            return TypeCheck(cwl_type=self, match=Match.No)

        fields_present = set(node.keys())
        missing_fields = required_fields - fields_present
        if len(missing_fields):
            return TypeCheck(cwl_type=self,
                             match=Match.Maybe, missing_req_fields=list(missing_fields))
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

        if node is None or isinstance(node, str):
            ln = LookupNode(loc=value_range)
            ln.intelligence_node = self
            code_intel.add_lookup_node(ln)

        if self.name == "Workflow":
            intel_context = Workflow()

        for k, child_node in node.items():

            if self.name == "WorkflowStep" and k == "run" and isinstance(child_node, str):
                # Exception for run field that is a string
                inferred_type = CWLLinkedFile(prefix=child_node, extension=".cwl")

            else:

                # Regular processing
                field = self.fields.get(k)
                if field is None:
                    if ":" not in k and k[0] != "$":
                        # heuristics to ignore $schemas, $namespaces and custom tags
                        problems += [
                            Diagnostic(
                                _range=node.lc.value(k),
                                message=f"Unknown field: {k} for type {self.name}",
                                severity=DiagnosticSeverity.Warning)
                        ]
                    continue

                else:
                    inferred_type = infer_type(child_node, field.types, key=k)

            inferred_type.parse(
                doc_uri=doc_uri,
                node=child_node,
                intel_context=intel_context,
                code_intel=code_intel,
                problems=problems,
                node_key=k,
                map_sp=map_sp,
                key_range=get_range_for_key(node, k),
                value_range=get_range_for_value(node, k),
                requirements=requirements)

    def completion(self):
        return [CompletionItem(label=k) for k in self.fields.keys()]


class CWLFieldType(CWLBaseType):

    def __init__(self, doc: str, required: bool, allowed_types: list):
        super().__init__("a field")
        self.doc = doc
        self.required = required
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types
