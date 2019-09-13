#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, IntelligenceContext, Intelligence, MapSubjectPredicate, TypeCheck, Match
from .unknowntype import CWLUnknownType
from .requirementstype import CWLRequirementsType
from ..langserver.lspobjects import Range
from ..code.requirements import Requirements
from ..code.intelligence import LookupNode, IntelligenceNode
from ..code.intelligencecontext import copy_context
from .lib import ListOrMap
from .typeinference import infer_type
from ..code import workflow


# TODO: subclass this to handle
#  inputs and outputs re: filling out keys = ports
#  requirements re: filling out types
#  To do this we need to properly propagate the name of the field to LOM types
#  and to properly handle the broken document that results when we start to fill
#  out a key

# A list or map type is almost always interesting (see docs/document-model.md)
# Requirements, step `in` and workflow `output` fields have special completions
# So for each of these we instantiate specialized types for the completers
# Parsing proceeds normally

class CWLListOrMapType(CWLBaseType):

    def __init__(self, name, allowed_types, map_sp: MapSubjectPredicate):
        super().__init__(name)
        self.map_subject_predicate = map_sp
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types
        self.enclosing_workflow = None

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if node is None or isinstance(node, (str, list, dict)):
            return TypeCheck(cwl_type=self)
        else:
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

        obj = ListOrMap(node, key_field=self.map_subject_predicate.subject, problems=problems)

        # items expressed as a map can have a special case
        # the key completer can be the completer for the subject field
        # if the value is a string, it's completer is the completer for the predicate field
        if self.name == "requirements":
            intel_context.requirements = IntelligenceNode(completions=[t.name for t in self.types])

        # Exception, when we have an empty LOM we assume it's gonna be a dict and
        # allow completions.
        # We end up with None or str when we just start a lom
        if obj.original_obj is None or isinstance(obj.original_obj, str):
            # TODO: remove redundancy
            # The keys get fancy completions
            if self.name == "requirements":
                ln = LookupNode(loc=value_range)
                ln.intelligence_node = intel_context.requirements
                code_intel.add_lookup_node(ln)

            elif self.name == "in":
                if intel_context.workflow_step_intelligence is not None:
                    ln = LookupNode(loc=value_range)
                    ln.intelligence_node = intel_context.workflow_step_intelligence.get_step_inport_completer()
                    code_intel.add_lookup_node(ln)

            elif self.name == "output":
                if intel_context.workflow is not None:
                    ln = LookupNode(loc=value_range)
                    ln.intelligence_node = intel_context.workflow.get_output_source_completer("")
                    code_intel.add_lookup_node(ln)

        for k, v in obj.as_dict.items():

            this_intel_context = copy_context(intel_context)
            this_intel_context.path += [k]

            inferred_type = infer_type(
                v,
                allowed_types=self.types,
                key=k if obj.was_dict else None,
                map_sp=self.map_subject_predicate if obj.was_dict else None)

            if self.name == "requirements" and isinstance(inferred_type, CWLUnknownType):
                # We've begun to type, and we can't formally infer this is a Requirement
                # but we'd like to offer auto-completions of requirement types
                inferred_type = CWLRequirementsType("requirement", self.types)

            if self.name == "steps":
                this_intel_context.workflow_step_intelligence = workflow.WFStepIntelligence(step_id=k)

            inferred_type.parse(
                doc_uri=doc_uri,
                node=v,
                intel_context=this_intel_context,
                code_intel=code_intel,
                problems=problems,
                node_key=k if obj.was_dict else None,
                map_sp=self.map_subject_predicate,
                key_range=obj.get_range_for_id(k),
                value_range=obj.get_range_for_value(k),
                requirements=requirements)

            if self.name == "steps":
                intel_context.workflow.add_step_intel(k, this_intel_context.workflow_step_intelligence)

            if obj.was_dict:
                # The keys get fancy completions
                if self.name == "requirements":
                    ln = LookupNode(loc=obj.get_range_for_id(k))
                    ln.intelligence_node = intel_context.requirements
                    code_intel.add_lookup_node(ln)

                elif self.name == "in":

                    wf_step = intel_context.workflow_step_intelligence
                    if wf_step is not None:

                        ln = LookupNode(loc=obj.get_range_for_id(k))
                        ln.intelligence_node = wf_step.get_step_inport_completer()
                        code_intel.add_lookup_node(ln)

                        if v is None or isinstance(v, str):
                            ln = LookupNode(loc=obj.get_range_for_value(k))
                            ln.intelligence_node = wf_step.get_step_source_completer(v)
                            code_intel.add_lookup_node(ln)

                elif self.name == "output":
                    if v is None or isinstance(v, str):
                        ln = LookupNode(loc=obj.get_range_for_value(k))
                        ln.intelligence_node = intel_context.workflow.get_output_source_completer(v)
                        code_intel.add_lookup_node(ln)
