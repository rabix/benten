#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, Workflow, Intelligence, MapSubjectPredicate, TypeCheck, Match
from ..langserver.lspobjects import Range, CompletionItem, Diagnostic, DiagnosticSeverity
from ..code.intelligence import LookupNode
from .lib import ListOrMap
from .typeinference import infer_type


# TODO: subclass this to handle
#  inputs and outputs re: filling out keys = ports
#  requirements re: filling out types
#  To do this we need to properly propagate the name of the field to LOM types
#  and to properly handle the broken document that results when we start to fill
#  out a key

# A list or map type is almost always interesting (see docs/document-model.md)
# Requirements, step `in` and workflow `output` fields have special completions
# So for each of these we instantiate specialized types. Depending on the exact

class CWLListOrMapType(CWLBaseType):

    def __init__(self, name, allowed_types, map_sp: MapSubjectPredicate):
        super().__init__(name)
        self.map_subject_predicate = map_sp
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types
        self.enclosing_workflow = None

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if isinstance(node, (list, dict)):
            return TypeCheck(cwl_type=self)
        else:
            return TypeCheck(cwl_type=self, match=Match.No)

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

        obj = ListOrMap(node, key_field=self.map_subject_predicate.subject, problems=problems)
        for k, v in obj.node.items():





    def parse2(self,
              doc_uri: str,
              node,
              value_lookup_node: ValueLookup,
              lom_key: str,
              parent_completer_node: CompleterNode,
              completer: Completer,
              problems: list, requirements=None):

        if isinstance(node, list):
            self.is_dict = False
            itr = enumerate(node)
        elif isinstance(node, dict):
            self.is_dict = True
            itr = node.items()
        else:
            # Incomplete document
            return

        for k, v in itr:

            if not self.is_dict and v is None:
                continue

            if self.is_dict:
                key_lookup_node = KeyLookup.from_key(node, k)
                key_lookup_node.completer_node = self
                completer.add_lookup_node(key_lookup_node)
            else:
                key_lookup_node = None

            value_lookup_node = ValueLookup.from_value(node, k)

            if self.name == "requirements":
                parent_completer_node = RequirementsCompleter([t.name for t in self.types])

            if self.name == "steps":
                step_id = k if self.is_dict else v.get("id")
                parent_completer_node = completer.wf_completer.get_step_completer(step_id)

            if self.name == "in":
                if self.is_dict:
                    key_lookup_node.completer_node = parent_completer_node.get_step_input_completer()
                    value_lookup_node.completer_node = parent_completer_node.parent
                    completer.add_lookup_node(value_lookup_node)

            lom_key = KeyField(self.map_subject_predicate, k) if self.is_dict else None
            inferred_type, type_check_results = infer_type(v, self.types, key_field=lom_key)

            add_to_problems(
                key_lookup_node.loc if key_lookup_node else value_lookup_node.loc,
                type_check_results, problems)

            inferred_type.parse(
                doc_uri=doc_uri,
                node=v,
                value_lookup_node=value_lookup_node,
                lom_key=lom_key,
                parent_completer_node=parent_completer_node,
                completer=completer,
                problems=problems,
                requirements=requirements)
