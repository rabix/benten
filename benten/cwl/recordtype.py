#  Copyright (c) 2019 Seven Bridges. See LICENSE

from typing import Dict

from .basetype import CWLBaseType, IntelligenceContext, Intelligence, MapSubjectPredicate, TypeCheck, Match
from .linkedfiletype import CWLLinkedFile
from .linkedschemadeftype import CWLLinkedSchemaDef
from .namespacedtype import CWLNameSpacedType
from ..langserver.lspobjects import Range, CompletionItem, Diagnostic, DiagnosticSeverity
from ..code.intelligence import LookupNode
from ..code.intelligencecontext import copy_context
from ..code.workflow import Workflow
from .typeinference import infer_type
from .lib import get_range_for_key, get_range_for_value
from ..code import workflow

import logging
logger = logging.getLogger(__name__)


class CWLRecordType(CWLBaseType):

    def __init__(self, name: str, doc: str, fields: Dict[str, 'CWLFieldType']):
        super().__init__(name)
        self.doc = doc
        self.fields = fields
        self.required_fields = set((k for k, v in self.fields.items() if v.required))
        self.all_fields = set(self.fields.keys())

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:

        if node is None:
            return TypeCheck(self, Match.No)

        # Exception for $import/$include etc.
        if isinstance(node, dict):
            if "$import" in node:
                if self.name == "InputRecordSchema":
                    return TypeCheck(cwl_type=CWLLinkedSchemaDef(node.get("$import")))
                else:
                    return TypeCheck(cwl_type=CWLLinkedFile(node.get("$import")))

        required_fields = self.required_fields - {map_sp.subject if map_sp else None}

        if not isinstance(node, dict):
            if map_sp is not None and node_key is not None:
                if map_sp.predicate in self.required_fields and len(required_fields) <= 1:
                    return TypeCheck(cwl_type=self)

            return TypeCheck(cwl_type=self, match=Match.No)

        fields_present = set(node.keys())
        missing_fields = required_fields - fields_present
        extra_fields = fields_present - self.all_fields
        if len(missing_fields):
            return TypeCheck(cwl_type=self,
                             match=Match.Maybe, missing_req_fields=list(missing_fields))
        elif len(extra_fields):
            return TypeCheck(cwl_type=self,
                             match=Match.Maybe)
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

        if not isinstance(node, dict):
            if map_sp is not None and map_sp.predicate is not None:
                _field_iterator = [(map_sp.predicate, node)]
            else:
                return
        else:
            _field_iterator = node.items()

        field_iterator = _put_requirements_first(_field_iterator)
        # We need to process the requirements first so that we resolve typedefs and JS libraries

        if self.name == "Workflow":
            intel_context.workflow = Workflow(node.get("inputs"), node.get("outputs"))

        for k, child_node in field_iterator:

            inferred_type = None
            this_intel_context = copy_context(intel_context)
            this_intel_context.path += [k]

            if isinstance(node, dict):
                key_range = get_range_for_key(node, k)
                value_range = get_range_for_value(node, k)

                # key completer
                ln = LookupNode(loc=key_range)
                ln.intelligence_node = self
                code_intel.add_lookup_node(ln)

            # TODO: looks like this logic and the logic in lomtype can be combined
            # Special completers

            # These paths tend to look like
            # ['requirements', 'XXRequirement', 'class']
            if k == "class" and len(this_intel_context.path) > 2 and \
                    this_intel_context.path[-3] == "requirements":
                ln = LookupNode(loc=value_range)
                ln.intelligence_node = this_intel_context.requirements
                code_intel.add_lookup_node(ln)

            if self.name == "WorkflowStep" and k == "run" and isinstance(child_node, str):
                # Exception for run field that is a string
                inferred_type = CWLLinkedFile(prefix=child_node, extension=".cwl")

            elif self.name == "InlineJavascriptRequirement" and k == "expressionLib":
                # todo: this will fail for inlined nested workflows
                code_intel.prepare_expression_lib(child_node)
                continue

            elif k in ["$schemas", "$namespaces"]:
                continue

            elif ":" in k:
                inferred_type = CWLNameSpacedType(k)

            else:

                # Regular processing
                field = self.fields.get(k)
                if field is None:
                    if ":" not in k and k[0] != "$":
                        # heuristics to ignore $schemas, $namespaces and custom tags
                        problems += [
                            Diagnostic(
                                _range=key_range,
                                message=f"Unknown field: {k} for type {self.name}",
                                severity=DiagnosticSeverity.Warning)
                        ]
                    continue

                else:
                    inferred_type = infer_type(child_node, field.types, key=k)

            inferred_type.parse(
                doc_uri=doc_uri,
                node=child_node,
                intel_context=this_intel_context,
                code_intel=code_intel,
                problems=problems,
                node_key=k,
                map_sp=map_sp,
                key_range=key_range,
                value_range=value_range,
                requirements=requirements)

            if self.name == "WorkflowOutputParameter" and k == "outputSource":
                ln = LookupNode(loc=value_range)
                ln.intelligence_node = this_intel_context.workflow.get_output_source_completer(child_node)
                code_intel.add_lookup_node(ln)

            if self.name == "WorkflowStepInput" and k == "source":
                ln = LookupNode(loc=value_range)
                ln.intelligence_node = this_intel_context.workflow_step_intelligence.get_step_source_completer(
                    child_node)
                code_intel.add_lookup_node(ln)

            if self.name == "WorkflowStep" and k == "run":
                if isinstance(inferred_type, CWLLinkedFile):
                    linked_process = inferred_type.node_dict
                else:
                    linked_process = child_node

                step_interface = workflow.parse_step_interface(linked_process, problems)
                intel_context.workflow_step_intelligence.set_step_interface(step_interface)

        if self.name == "Workflow":
            intel_context.workflow.validate_connections(node.get("steps"), problems=problems)

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


def _put_requirements_first(_field_iterator):
    field_iterator = []
    for k, v in _field_iterator:
        if k == "requirements":
            field_iterator = [(k, v)]
            break
    for k, v in _field_iterator:
        if k != "requirements":
            field_iterator += [(k, v)]
    return field_iterator
