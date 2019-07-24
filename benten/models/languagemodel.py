"""Create completion/validation code from the JSON schema.

We create CWL Type objects from the CWL JSON schema.
These types don't do much. These are subclassed in
parser.py to perform validations and create completers

For details see ../../docs/document-model.md
"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from typing import Union, List, Dict
import json
import pathlib
import urllib.parse
from dataclasses import dataclass
from enum import IntEnum
import shlex

from ruamel.yaml import YAML
fast_load = YAML(typ='safe')

from ..langserver.lspobjects import (
    Position, Range, Location, CompletionItem, Diagnostic, DiagnosticSeverity)
from .intelligence import (KeyLookup, ValueLookup, CompleterNode, Completer, Style)
from .symbols import extract_symbols, extract_step_symbols
from . import workflow


import logging
logger = logging.getLogger(__name__)


latest_published_cwl_version = "v1.0"


# Methods to parse the language model

def load_languagemodel(fname):
    lang_model = {}
    schema = json.load(open(fname, "r"))
    parse_cwl_type(schema, lang_model)
    parse_cwl_type(schema, lang_model)  # Two passes takes care of forward references
    clean_up_model(lang_model)
    return lang_model


# CWL grows hairy. It needs to be shaved periodically
def clean_up_model(lang_model):
    if isinstance(lang_model.get("CWLVersion"), CWLEnumType):
        lang_model["CWLVersion"].symbols = [
            symbol
            for symbol in lang_model["CWLVersion"].symbols
            if not symbol.startswith("draft-")
        ]
        lang_model["CWLVersion"].symbols.remove("v1.0.dev4")
        return

    logger.error("No CWLVersion enum in schema")


def parse_cwl_type(schema, lang_model, map_subject_predicate=None, field_name=None):

    if isinstance(schema, str):
        return lang_model.get(schema, schema)

    elif isinstance(schema, list):
        return [
            parse_cwl_type(_scheme, lang_model, map_subject_predicate, field_name)
            for _scheme in schema
        ]

    elif schema.get("type") == "array":
        name = field_name  # schema.get("name")
        if map_subject_predicate is None:
            return CWLArrayType(
                name=name,
                allowed_types=parse_cwl_type(schema.get("items"), lang_model))
        else:
            return CWLListOrMapType(
                name=name,
                allowed_types=parse_cwl_type(schema.get("items"), lang_model),
                lom_key=map_subject_predicate)

    elif schema.get("type") == "enum":
        return parse_enum(schema, lang_model)

    elif schema.get("type") == "record":
        return parse_record(schema, lang_model)

    logger.error(f"Unknown schema type {schema.get('type')}: {schema}")


def parse_enum(schema, lang_model):
    enum_name = schema.get("name")

    if enum_name == "Any":
        # This is a special type masquerading as an enum
        lang_model[enum_name] = CWLAnyType(name=schema.get("name"))
        return lang_model.get(enum_name)

    symbols = schema.get("symbols")
    for extends in listify(schema.get("extends")):
        extends = extends.split("#")[1]  # Proper way is to use URIs ...
        if extends in lang_model:
            symbols += lang_model[extends].symbols

    lang_model[enum_name] = CWLEnumType(
        name=schema.get("name"),
        doc=schema.get("doc"),
        symbols=set(symbols))

    return lang_model.get(enum_name)


def parse_record(schema, lang_model):
    record_name = schema.get("name")
    fields = {}
    for extends in listify(schema.get("extends")):
        extends = extends.split("#")[1]  # Proper way is to use URIs ...
        if extends in lang_model:
            fields.update(**lang_model[extends].fields)

    fields.update(**{
        k: v
        for field in schema.get("fields") for k, v in [parse_field(field, lang_model)]
    })

    lang_model[record_name] = CWLRecordType(
        name=record_name,
        doc=schema.get("doc"),
        fields=fields)

    return lang_model.get(record_name)


def listify(items):
    if items is None:
        return []
    elif isinstance(items, list):
        return items
    else:
        return [items]


class MapSubjectPredicate:

    def __init__(self, subject, predicate):
        self.subject = subject
        self.predicate = predicate


def parse_field(field, lang_model):

    field_name = field.get("name")
    required = True
    _allowed_types = field.get("type")
    if isinstance(_allowed_types, list) and "null" in _allowed_types:
        required = False

    map_subject_predicate = None
    jldp = field.get("jsonldPredicate")
    if isinstance(jldp, dict):
        map_subject_predicate = MapSubjectPredicate(jldp.get("mapSubject"), jldp.get("mapPredicate"))

    return field_name, CWLFieldType(
        doc=field.get("doc"),
        required=required,
        allowed_types=parse_cwl_type(
            _allowed_types, lang_model,
            map_subject_predicate=map_subject_predicate,
            field_name=field_name)
    )


# Methods to parse the CWL document


def infer_model_from_type(doc: dict, lang_model: dict):
    if "class" in doc:
        return lang_model.get(doc.get("class"))

    if "type" in doc:
        return lang_model.get(doc.get("type"))


process_types = ["CommandLineTool", "ExpressionTool", "Workflow"]


def parse_document(cwl: dict, doc_uri: str, raw_text: str, lang_models: dict, problems: List=None):

    completer = Completer()
    symbols = {}

    line_count = len(raw_text.splitlines())

    if isinstance(cwl, dict):

        cwl_v = cwl.get("cwlVersion")
        if not isinstance(cwl_v, str):
            cwl_v = latest_published_cwl_version

        lm = lang_models.get(cwl_v)
        if lm is None:
            logger.error(f"No language model for cwl version {cwl_v}. Using {latest_published_cwl_version}")
            lm = lang_models.get(latest_published_cwl_version)

        _typ = cwl.get("class")
        if _typ is not None:
            base_type = lm.get(_typ)
            value_lookup_node = ValueLookup(Range(Position(0, 0), Position(0, 0)))
            if base_type is not None:
                base_type.parse(
                    doc_uri=doc_uri,
                    node=cwl,
                    value_lookup_node=value_lookup_node,
                    lom_key=None,
                    parent_completer_node=None,
                    completer=completer,
                    problems=problems,
                    requirements=None)

        if _typ in process_types:
            symbols = extract_symbols(cwl, line_count)

            if _typ == "Workflow":
                symbols = extract_step_symbols(cwl, symbols)
                wf_graph = workflow.analyze_connectivity(completer, problems)


    return completer, list(symbols.values()), problems


@dataclass
class KeyField:
    map_subject_predicate: MapSubjectPredicate
    key: str


class TypeMatch(IntEnum):
    MatchAndValid = 1
    MatchButInvalid = 2
    PossibleMatch = 3
    NotMatch = 4


# This allows us to quantify how well a type matches. This is
# used for type inference heuristics
@dataclass
class TypeTestResult:
    cwl_type: Union[None, 'CWLBaseType']
    match_type: TypeMatch
    missing_required_fields: list
    message: Union[None, str] = None


def infer_type(node, allowed_types, key_field=None):

    type_check_results = []

    explicit_type = get_explicit_type_str(node, key_field)

    if explicit_type is not None:
        for _type in allowed_types:
            if explicit_type == _type.name:
                return _type, None
        else:
            return CWLUnknownType(), [
                TypeTestResult(
                    cwl_type=None,
                    match_type=TypeMatch.NotMatch,
                    missing_required_fields=[],
                    message=f"Found {explicit_type}. "
                    f"Expected one of {[t.name for t in allowed_types]}"
                )
            ]

    for _type in allowed_types:
        if _type == 'null':
            if node is None:
                return CWLScalarType(), None
            else:
                continue

        # For now, don't closely validate these base types
        if _type in ['string', 'boolean', 'int', 'long']:
            if node is None or isinstance(node, str):
                return CWLScalarType(), None
            else:
                continue

        check_result = _type.check(node, key_field)

        if check_result.match_type == TypeMatch.MatchAndValid:
            return check_result.cwl_type, None

        if check_result.match_type == TypeMatch.MatchButInvalid:
            return check_result.cwl_type, check_result

        type_check_results += [check_result]

    # There is only one possible type here
    if len(type_check_results) == 1:
        return type_check_results[0].cwl_type, type_check_results[0]

    # OK. We don't have a match. For now we will not use any heuristics to guess
    # We'll return an Unknown type for now
    return CWLUnknownType(), type_check_results


def get_explicit_type_str(node, key_field: KeyField):
    if key_field is not None:
        if key_field.map_subject_predicate.subject == "class":
            return key_field.key
        else:
            return None
    elif isinstance(node, dict):
        return node.get("class")
    else:
        return None


def add_to_problems(loc, type_check_results, problems):
    if type_check_results is not None:
        if isinstance(type_check_results, list):
            message = "Unknown type: " + "\n".join(em.message for em in type_check_results)
        else:
            message = type_check_results.message

        problems += [
            Diagnostic(
                _range=loc,
                message=message,
                severity=DiagnosticSeverity.Error)
        ]


class CWLBaseType:

    def parse(self,
              doc_uri: str,
              node,
              value_lookup_node: ValueLookup,
              parent_completer_node: CompleterNode,
              lom_key: MapSubjectPredicate,
              completer: Completer,
              problems: list, requirements=None):
        pass

    def definition(self):
        pass

    def completion(self):
        pass

    @staticmethod
    def resolve_file_path(doc_uri, target_path):
        _path = pathlib.PurePosixPath(target_path)
        if not _path.is_absolute():
            base_path = pathlib.Path(urllib.parse.urlparse(doc_uri).path).parent
        else:
            base_path = "."
        _path = pathlib.Path(base_path / _path).resolve().absolute()
        return _path


class CWLScalarType(CWLBaseType):

    def parse(self,
              doc_uri: str,
              node,
              value_lookup_node: ValueLookup,
              lom_key: MapSubjectPredicate,
              parent_completer_node: CompleterNode,
              completer: Completer,
              problems: list, requirements=None):

        # this_completer_node = IntelligenceNode(
        #     indent=value_lookup_node.loc.start.character,
        #     style=Style.none,
        #     completions=[],
        #     parent=parent_completer_node
        # )

        # value_lookup_node.intelligence_node = this_completer_node
        completer.add_lookup_node(value_lookup_node)
        # code_intelligence.add_intelligence_node(this_completer_node)


class CWLUnknownType(CWLBaseType):
    pass


class CWLLinkedFile(CWLBaseType):

    def __init__(self, linked_file: str):
        self.doc_uri = None
        self.linked_file = linked_file
        self.full_path = None

    def parse(self,
              doc_uri: str,
              node: str,
              value_lookup_node: ValueLookup,
              lom_key: MapSubjectPredicate,
              parent_completer_node: CompleterNode,
              completer: Completer,
              problems: list, requirements=None):

        self.doc_uri = doc_uri

        self.full_path = self.resolve_file_path(self.doc_uri, self.linked_file)
        if not self.full_path.exists():
            problems += [
                Diagnostic(
                    _range=value_lookup_node.loc,
                    message=f"Missing linked file {self.linked_file}",
                    severity=DiagnosticSeverity.Error)
            ]

        value_lookup_node.completer_node = self
        completer.add_lookup_node(value_lookup_node)

    def definition(self):
        return Location(self.full_path.as_uri())

    def completion(self):
        return [
            CompletionItem(label=file_path)
            for file_path in self._file_picker(self.linked_file)
        ]

    def _file_picker(self, prefix):

        # We use .split( ... ) so we can handle the case for run: .    # my/commented/path
        # an other such shenanigans
        _prefix = shlex.split(prefix, comments=True)[0]

        path = self.full_path
        if not path.is_dir():
            path = path.parent

        if not path.exists():
            logger.error(f"No path called: {path}")
            return []

        # This is a workaround to the issue of having a dangling "." in front of the path
        pre = "/" if _prefix in [".", ".."] else ""

        return (pre + str(p.relative_to(path))
                for p in path.iterdir()
                if p.is_dir() or p.suffix == ".cwl")


class CWLLinkedProcessFile(CWLLinkedFile):
    # This helps us to identify steps
    pass


class CWLStepInputs(CWLBaseType):
    # This helps auto-complete input port names
    pass


class CWLSource(CWLBaseType):
    # This helps auto-complete source port names
    pass


class CWLStepOutputs(CWLBaseType):
    # This helps auto-complete output port names
    pass


class CWLAnyType(CWLBaseType):

    def __init__(self, name: str):
        self.name = name

    def check(self, node, lom_key: MapSubjectPredicate=None):

        # Special treatment for the any type. It agrees to everything
        return TypeTestResult(
            cwl_type=self,
            match_type=TypeMatch.MatchAndValid,
            missing_required_fields=[],
            message=""
        )

    def parse(self,
              doc_uri: str,
              node,
              value_lookup_node: ValueLookup,
              lom_key: MapSubjectPredicate,
              parent_completer_node: CompleterNode,
              completer: Completer,
              problems: list, requirements=None):

        value_lookup_node.completer_node = self
        completer.add_lookup_node(value_lookup_node)


class CWLEnumType(CWLBaseType):

    def __init__(self, name: str, doc: str, symbols: set):
        self.name = name
        self.doc = doc
        self.symbols = symbols

    def __str__(self):
        return str(self.symbols)

    def __repr__(self):
        return str(self)

    def check(self, node, lom_key: MapSubjectPredicate=None):

        if not (isinstance(node, str) or None):
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.NotMatch,
                missing_required_fields=[],
                message="Expecting an enum value here"
            )

        symbols = self.symbols
        if self.name in ["PrimitiveType", "CWLType"]:
            # Special treatment for syntactic sugar around types
            symbols = [
                sy + ext for sy in self.symbols for ext in ["", "[]", "?", "[]?"]
            ]

        if node not in symbols:
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.MatchButInvalid,
                missing_required_fields=[],
                message=f"Expecting one of {self.symbols}"
            )

        return TypeTestResult(
            cwl_type=self,
            match_type=TypeMatch.MatchAndValid,
            missing_required_fields=[],
            message=None
        )

    def parse(self,
              doc_uri: str,
              node,
              value_lookup_node: ValueLookup,
              lom_key: MapSubjectPredicate,
              parent_completer_node: CompleterNode,
              completer: Completer,
              problems: list, requirements=None):

        value_lookup_node.completer_node = self
        completer.add_lookup_node(value_lookup_node)

    def completion(self):
        return [CompletionItem(label=s) for s in self.symbols]


class CWLArrayType(CWLBaseType):

    def __init__(self, name, allowed_types):
        self.name = name
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types

    def __str__(self):
        return str(self.types)

    def __repr__(self):
        return str(self)

    def check(self, node, lom_key: MapSubjectPredicate=None):

        if isinstance(node, list):
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.MatchAndValid,
                missing_required_fields=[],
                message=None
            )
        else:
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.NotMatch,
                missing_required_fields=[],
                message=None
            )

    def parse(self,
              doc_uri: str,
              node,
              value_lookup_node: ValueLookup,
              lom_key: MapSubjectPredicate,
              parent_completer_node: CompleterNode,
              completer: Completer,
              problems: list, requirements=None):

        for n in range(len(node)):
            value_lookup_node = ValueLookup.from_value(node, n)

            # loc = node.lc.item(n)
            # style = Style.flow if node[n].fa.flow_style() else Style.block
            inferred_type, type_check_results = infer_type(node[n], self.types, key_field=None)
            add_to_problems(value_lookup_node.loc, type_check_results, problems)
            inferred_type.parse(
                doc_uri=doc_uri,
                node=node[n],
                value_lookup_node=value_lookup_node,
                lom_key=lom_key,
                parent_completer_node=parent_completer_node,
                completer=completer,
                problems=problems,
                requirements=requirements)


# TODO: subclass this to handle
#  inputs and outputs re: filling out keys = ports
#  requirements re: filling out types
#  To do this we need to properly propagate the name of the field to LOM types
#  and to properly handle the broken document that results when we start to fill
#  out a key
class CWLListOrMapType(CWLBaseType):

    def __init__(self, name, allowed_types, lom_key):
        self.name = name
        self.is_dict = None
        self.map_subject_predicate = lom_key
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types

    def check(self, node, lom_key: MapSubjectPredicate=None):

        if isinstance(node, (list, dict)):
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.MatchAndValid,
                missing_required_fields=[],
                message=None
            )
        else:
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.NotMatch,
                missing_required_fields=[],
                message=None
            )

    def parse(self,
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


class RequirementsCompleter(CompleterNode):

    def __init__(self, req_types):
        super().__init__(completions=req_types)


class CWLRecordType(CWLBaseType):

    def __init__(self, name: str, doc: str, fields: Dict[str, 'CWLFieldType']):
        self.name = name
        self.doc = doc
        self.fields = fields
        self.required_fields = set((k for k, v in self.fields.items() if v.required))

    def __str__(self):
        return f"{self.name}: {str(self.fields)}"

    def __repr__(self):
        return str(self)

    def check(self, node, key_field: KeyField=None):

        if node is None:
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.NotMatch,
                missing_required_fields=list(self.required_fields),
                message=f"Tried type {self.name}: Got NONE"
            )

        # Exception for $import/$include etc.
        if isinstance(node, dict):
            if "$import" in node:
                return TypeTestResult(
                    cwl_type=CWLLinkedFile(linked_file=node.get("$import")),
                    match_type=TypeMatch.MatchAndValid,
                    missing_required_fields=[]
                )

        required_fields = self.required_fields - {key_field.map_subject_predicate.subject if key_field else None}

        if isinstance(node, str):
            if key_field is not None:
                if key_field.map_subject_predicate.predicate in self.fields and len(required_fields) <= 1:
                    return TypeTestResult(
                                cwl_type=self,
                                match_type=TypeMatch.MatchAndValid,
                                missing_required_fields=[],
                                message=None
                            )
                else:
                    return TypeTestResult(
                                cwl_type=self,
                                match_type=TypeMatch.NotMatch,
                                missing_required_fields=list(self.required_fields),
                                message=f"Tried type {self.name}: Got string"
                            )
            else:
                return TypeTestResult(
                    cwl_type=self,
                    match_type=TypeMatch.NotMatch,
                    missing_required_fields=list(self.required_fields),
                    message=f"Tried type {self.name}: Got string"
                )

        if not isinstance(node, dict):
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.NotMatch,
                missing_required_fields=list(self.required_fields),
                message=f"Tried type {self.name}: Got {type(node)}"
            )

        fields_present = set(node.keys())
        missing_fields = required_fields - fields_present
        if len(missing_fields):
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.PossibleMatch,
                missing_required_fields=list(missing_fields),
                message=""
            )
        else:
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.MatchAndValid,
                missing_required_fields=list(missing_fields),
                message=""
            )

    def parse(self,
              doc_uri: str,
              node,
              value_lookup_node: ValueLookup,
              parent_completer_node: CompleterNode,
              lom_key: MapSubjectPredicate,
              completer: Completer,
              problems: list, requirements=None):

        if isinstance(node, str) or node is None:
            # value_lookup_node.intelligence_node = this_completer_node
            return

        if self.name == "Workflow":
            completer.wf_completer = WF_Completer()
            completer.wf_completer.analyze_workflow(node, doc_uri, problems)

        for k, child_node in node.items():

            key_lookup_node = KeyLookup.from_key(node, k)
            key_lookup_node.completer_node = self
            completer.add_lookup_node(key_lookup_node)
            value_lookup_node = ValueLookup.from_value(node, k)

            if self.name == "WorkflowStep" and k == "run" and isinstance(child_node, str):
                # Exception for run field that is a string
                inferred_type = CWLLinkedProcessFile(linked_file=child_node)

            else:

                # Regular processing
                field = self.fields.get(k)
                if field is None:
                    if ":" not in k and k[0] != "$":
                        # heuristics to ignore $schemas, $namespaces and custom tags
                        problems += [
                            Diagnostic(
                                _range=key_lookup_node.loc,
                                message=f"Unknown field: {k} for type {self.name}",
                                severity=DiagnosticSeverity.Warning)
                        ]
                    continue

                else:
                    inferred_type, type_check_results = infer_type(child_node, field.types, key_field=lom_key)
                    add_to_problems(value_lookup_node.loc, type_check_results, problems)

            inferred_type.parse(
                doc_uri=doc_uri,
                node=child_node,
                value_lookup_node=value_lookup_node,
                lom_key=lom_key,
                parent_completer_node=parent_completer_node,
                completer=completer,
                problems=problems,
                requirements=requirements)

    def completion(self):
        return [CompletionItem(label=k) for k in self.fields.keys()]


class CWLFieldType(CWLBaseType):

    def __init__(self, doc: str, required: bool, allowed_types: list):
        self.doc = doc
        self.required = required
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types

    def __str__(self):
        return str(self.types)

    def __repr__(self):
        return str(self)


class WF_Completer(CompleterNode):

    def __init__(self, *args):
        super().__init__(*args)
        self.step_interface = {}
        self.wf_inputs = []
        self.all_connections = []

    # TODO: refactor this, because of redundant code and processing
    def analyze_workflow(self, node, doc_uri, problems):

        _steps = node.get("steps")
        # Convert it all to a dict for ease of processing
        if isinstance(_steps, dict):
            steps = _steps
        elif isinstance(_steps, list):
            steps = {}
            for n, _step in enumerate(_steps):
                if isinstance(_step, dict):
                    _step_id = _step.get("id")
                    if _step_id is not None:
                        steps[_step_id] = _step  # This still has location information
                    else:
                        problems += [
                            Diagnostic(
                                _range=get_range_for_value(_steps, n),
                                message=f"Step has no id",
                                severity=DiagnosticSeverity.Error)
                        ]
        else:
            return

        for step_id, step in steps.items():
            if isinstance(step, dict):
                self.step_interface[step_id] = parse_step_interface(doc_uri, step)

        self.wf_inputs = list_as_map(node.get("inputs"), key_field="id")
        self.all_connections = self.generate_all_possible_connections()

        for step_id, step in steps.items():
            if isinstance(step, dict):
                self.validate_step_connections(step, step_id, problems)

    def generate_all_possible_connections(self):
        step_ports = [f"{step}/{port}"
                      for step in self.step_interface.keys()
                      for port in self.step_interface[step]["outputs"]]
        wf_inputs = [f"{inp}" for inp in self.wf_inputs.keys()]
        return set(step_ports + wf_inputs)

    def validate_step_connections(self, step, step_id, problems):
        inputs = step.get("in")
        allowed_inputs = set(self.step_interface[step_id]["inputs"])

        if isinstance(inputs, list):
            is_dict = False
            itr = enumerate(inputs)
        elif isinstance(inputs, dict):
            is_dict = True
            itr = inputs.items()
        else:
            return

        for k, v in itr:
            if is_dict:
                input_id = k
                id_range = get_range_for_key(inputs, k)
            else:
                input_id = v.get("id")
                id_range = get_range_for_value(inputs, k)

            if input_id not in allowed_inputs:
                problems += [
                    Diagnostic(
                        _range=id_range,
                        message=f"Expecting one of {allowed_inputs}",
                        severity=DiagnosticSeverity.Error)
                ]

            if isinstance(v, dict):
                conn_id = v.get("source")
                if conn_id is None:
                    continue
                conn_range = get_range_for_value(v, "source")
            elif isinstance(v, str):
                conn_id = v
                conn_range = get_range_for_value(inputs, k)
            else:
                continue

            if conn_id not in self.all_connections:
                problems += [
                    Diagnostic(
                        _range=conn_range,
                        message=f"No such source",
                        severity=DiagnosticSeverity.Error)
                ]

    def get_step_completer(self, step_id):
        return WFStepCompleter(parent=self, step_id=step_id, step_interface=self.step_interface)

    def completion(self):
        # step_ports = [CompletionItem(label=f"{step}/{port}")
        #               for step in self.step_interface.keys()
        #               for port in self.step_interface[step]["outputs"]]
        # wf_inputs = [CompletionItem(label=f"{inp}") for inp in self.wf_inputs.keys()]

        return [CompletionItem(label=v) for v in self.all_connections]


class WFStepCompleter(CompleterNode):
    def __init__(self, parent, step_id, step_interface):
        super().__init__()
        self.parent = parent
        self.step_id = step_id
        self.step_interface = step_interface

    def get_step_input_completer(self):
        return WFStepInputCompleter(inputs=self.step_interface[self.step_id]["inputs"])

    def get_step_output_completer(self):
        return WFStepOutputCompleter(outputs=self.step_interface[self.step_id]["outputs"])


class WFStepInputCompleter(CompleterNode):
    def __init__(self, inputs):
        super().__init__(completions=inputs)


class WFStepOutputCompleter(CompleterNode):
    def __init__(self, outputs):
        super().__init__(completions=outputs)


def parse_step_interface(doc_uri, step):

    run_field = step.get("run")

    if isinstance(run_field, str):
        _step_path = resolve_file_path(doc_uri, run_field)
        if _step_path.exists() and _step_path.is_file():
            run_field = fast_load.load(_step_path)

    inputs = []
    outputs = []
    if isinstance(run_field, dict):
        inputs = [k for k in list_as_map(run_field.get("inputs"), key_field="id").keys()]
        outputs = [k for k in list_as_map(run_field.get("outputs"), key_field="id").keys()]

    return {
        "inputs": inputs,
        "outputs": outputs
    }


def get_range_for_key(parent, key):
    start = parent.lc.key(key)
    end = (start[0], start[1] + len(key))
    return Range(Position(*start), Position(*end))


# TODO: refactor this for redundancy
def get_range_for_value(node, key):
    if isinstance(node, dict):
        start = node.lc.value(key)
    else:
        start = node.lc.item(key)

    v = node[key]
    if v is None:
        v = ""
    else:
        v = str(v)  # How to handle multi line strings

    end = (start[0], start[1] + len(v))
    return Range(Position(*start), Position(*end))


def resolve_file_path(doc_uri, target_path):
    _path = pathlib.PurePosixPath(target_path)
    if not _path.is_absolute():
        base_path = pathlib.Path(urllib.parse.urlparse(doc_uri).path).parent
    else:
        base_path = "."
    _path = pathlib.Path(base_path / _path).resolve().absolute()
    return _path


def list_as_map(node, key_field):
    if isinstance(node, dict):
        return node

    new_node = {}

    if isinstance(node, list):
        for _item in node:
            if isinstance(_item, dict):
                key = _item.get(key_field)
                if key is not None:
                    new_node[key] = _item

    return new_node



# ## Use as ##
# import json
# fname = 'schema.json'
# schema = json.load(open(fname, "r"))
# lang_model = {}
# parse_cwl_type(schema, lang_model)
