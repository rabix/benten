"""Create completion/validation code from the JSON schema.

We create CWL Type objects from the CWL JSON schema.
These types don't do much. These are subclassed in
parser.py to perform validations and create completers

For details see ../../docs/document-model.md
"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from typing import Union, List, Dict
import json
from abc import abstractmethod
from dataclasses import dataclass
from enum import IntEnum

from ..langserver.lspobjects import (
    Position, Range, CompletionItem, Diagnostic, DiagnosticSeverity)
from .completer import (KeyLookup, ValueLookup, CompleterNode, Completer, Style)


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


def parse_cwl_type(schema, lang_model, lom_key=None):

    if isinstance(schema, str):
        return lang_model.get(schema, schema)

    elif isinstance(schema, list):
        return [
            parse_cwl_type(_scheme, lang_model, lom_key)
            for _scheme in schema
        ]

    elif schema.get("type") == "array":
        if lom_key is None:
            return CWLArrayType(parse_cwl_type(schema.get("items"), lang_model))
        else:
            return CWLListOrMapType(parse_cwl_type(schema.get("items"), lang_model), lom_key=lom_key)

    elif schema.get("type") == "enum":
        return parse_enum(schema, lang_model)

    elif schema.get("type") == "record":
        return parse_record(schema, lang_model)

    logger.error(f"Unknown schema type {schema.get('type')}: {schema}")


def parse_enum(schema, lang_model):
    enum_name = schema.get("name")
    if True: # enum_name not in lang_model:
        lang_model[enum_name] = CWLEnumType(
            name=schema.get("name"),
            doc=schema.get("doc"),
            symbols=schema.get("symbols"))

    return lang_model.get(enum_name)


def parse_record(schema, lang_model):
    record_name = schema.get("name")
    if True: # record_name not in lang_model:
        lang_model[record_name] = CWLRecordType(
            name=record_name,
            doc=schema.get("doc"),
            fields={
                k: v
                for field in schema.get("fields") for k, v in [parse_field(field, lang_model)]
            })

    return lang_model.get(record_name)


class LomKey:

    def __init__(self, subject, predicate):
        self.subject = subject
        self.predicate = predicate


def parse_field(field, lang_model):

    field_name = field.get("name")
    required = True
    _allowed_types = field.get("type")
    if isinstance(_allowed_types, list) and "null" in _allowed_types:
        required = False

    lom_key = None
    jldp = field.get("jsonldPredicate")
    if isinstance(jldp, dict):
        lom_key = LomKey(jldp.get("mapSubject"), jldp.get("mapPredicate"))

    return field_name, CWLFieldType(
        doc=field.get("doc"),
        required=required,
        allowed_types=parse_cwl_type(_allowed_types, lang_model, lom_key=lom_key)
    )


# Methods to parse the CWL document


def infer_model_from_type(doc: dict, lang_model: dict):
    if "class" in doc:
        return lang_model.get(doc.get("class"))

    if "type" in doc:
        return lang_model.get(doc.get("type"))


def parse_document(cwl: dict, lang_models: dict, problems: List=None):

    completer = Completer()

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
                    node=cwl,
                    value_lookup_node=value_lookup_node,
                    lom_key=None,
                    parent_completer_node=None,
                    completer=completer,
                    problems=problems,
                    requirements=None)

        return completer, problems


class TypeMatch(IntEnum):
    MatchAndValid = 1
    MatchButInvalid = 2
    PossibleMatch = 3
    NotMatch = 4


# This allows us to quantify how well a type matches. This is
# used for type inference heuristics
@dataclass
class TypeTestResult:
    cwl_type: 'CWLBaseType'
    match_type: TypeMatch
    missing_required_fields: list
    message: Union[None, str]


def infer_type(node, allowed_types, lom_key=None):

    type_check_results = []

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

        check_result = _type.check(node, lom_key)

        if check_result.match_type == TypeMatch.MatchAndValid:
            return _type, None

        if check_result.match_type == TypeMatch.MatchButInvalid:
            return _type, check_result

        type_check_results += [check_result]

    # There is only one possible type here
    if len(type_check_results) == 1:
        return type_check_results[0].cwl_type, type_check_results[0]

    # OK. We don't have a match. For now we will not use any heuristics to guess
    # We'll return an Unknown type for now
    return CWLUnknownType(), type_check_results


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
    pass


class CWLScalarType(CWLBaseType):

    def parse(self,
              node,
              value_lookup_node: ValueLookup,
              lom_key: LomKey,
              parent_completer_node: CompleterNode,
              completer: Completer,
              problems: list, requirements=None):

        this_completer_node = CompleterNode(
            indent=value_lookup_node.loc.start.character,
            style=Style.none,
            completions=[],
            parent=parent_completer_node
        )

        value_lookup_node.completer_node = this_completer_node
        completer.add_lookup_node(value_lookup_node)
        completer.add_completer_node(this_completer_node)


class CWLUnknownType(CWLBaseType):
    pass


class CWLEnumType(CWLBaseType):

    def __init__(self, name: str, doc: str, symbols: list):
        self.name = name
        self.doc = doc
        self.symbols = symbols

    def __str__(self):
        return str(self.symbols)

    def __repr__(self):
        return str(self)

    def check(self, node, lom_key: LomKey=None):

        if not (isinstance(node, str) or None):
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.NotMatch,
                missing_required_fields=[],
                message="Expecting an enum value here"
            )

        if node not in self.symbols:
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
              node,
              value_lookup_node: ValueLookup,
              lom_key: LomKey,
              parent_completer_node: CompleterNode,
              completer: Completer,
              problems: list, requirements=None):

        this_completer_node = CompleterNode(
            indent=value_lookup_node.loc.start.character,
            style=Style.none,
            completions=self.symbols,
            parent=parent_completer_node
        )

        value_lookup_node.completer_node = this_completer_node
        completer.add_lookup_node(value_lookup_node)
        completer.add_completer_node(this_completer_node)


class CWLArrayType(CWLBaseType):

    def __init__(self, allowed_types):
        self.name = "list"
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types

    def __str__(self):
        return str(self.types)

    def __repr__(self):
        return str(self)

    def check(self, node, lom_key: LomKey=None):

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
              node,
              value_lookup_node: ValueLookup,
              lom_key: LomKey,
              parent_completer_node: CompleterNode,
              completer: Completer,
              problems: list, requirements=None):

        for n in range(len(node)):
            value_lookup_node = ValueLookup.from_value(node, n)

            # loc = node.lc.item(n)
            # style = Style.flow if node[n].fa.flow_style() else Style.block
            inferred_type, type_check_results = infer_type(node[n], self.types, lom_key=None)
            add_to_problems(value_lookup_node.loc, type_check_results, problems)
            inferred_type.parse(
                node=node[n],
                value_lookup_node=value_lookup_node,
                parent_completer_node=parent_completer_node,
                completer=completer,
                problems=problems,
                requirements=requirements)


class CWLListOrMapType(CWLBaseType):

    def __init__(self, allowed_types, lom_key):
        self.name = "list/map"
        self.lom_key = lom_key
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types

    def check(self, node, lom_key: LomKey=None):

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
              node,
              value_lookup_node: ValueLookup,
              lom_key: LomKey,
              parent_completer_node: CompleterNode,
              completer: Completer,
              problems: list, requirements=None):

        if isinstance(node, list):
            itr = enumerate(node)
            loc_fn = node.lc.item
            lom_key = None
        elif isinstance(node, dict):
            itr = node.items()
            loc_fn = node.lc.value
            lom_key = self.lom_key
        else:
            # Incomplete document
            return

        for k, v in itr:
            value_lookup_node = ValueLookup.from_value(node, k)

            inferred_type, type_check_results = infer_type(v, self.types, lom_key=lom_key)
            add_to_problems(value_lookup_node.loc, type_check_results, problems)
            inferred_type.parse(
                node=v,
                value_lookup_node=value_lookup_node,
                lom_key=lom_key,
                parent_completer_node=parent_completer_node,
                completer=completer,
                problems=problems,
                requirements=requirements)


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

    def check(self, node, lom_key: LomKey=None):

        if node is None:
            return TypeTestResult(
                cwl_type=self,
                match_type=TypeMatch.NotMatch,
                missing_required_fields=list(self.required_fields),
                message=f"Tried type {self.name}: Got NONE"
            )

        required_fields = self.required_fields - {lom_key.subject if lom_key else None}

        if isinstance(node, str):
            if lom_key is not None:
                if lom_key.predicate in self.fields and len(required_fields) <= 1:
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
              node,
              value_lookup_node: ValueLookup,
              parent_completer_node: CompleterNode,
              lom_key: LomKey,
              completer: Completer,
              problems: list, requirements=None):

        if isinstance(node, str) or node is None:
            # This is expressed in abbreviated form
            # In some cases we'll have a custom completer
            completions = []
        else:
            completions = list(set(self.fields.keys()) - set(node.keys()))

        this_completer_node = CompleterNode(
            indent=value_lookup_node.loc.start.character,
            style=Style.none,
            completions=completions,
            parent=parent_completer_node
        )
        completer.add_completer_node(this_completer_node)

        if isinstance(node, str) or node is None:
            value_lookup_node.completer_node = this_completer_node
            return

        for k, child_node in node.items():

            key_lookup_node = KeyLookup.from_key(node, k)
            key_lookup_node.completer_node = this_completer_node
            completer.add_lookup_node(key_lookup_node)

            value_lookup_node = ValueLookup.from_value(node, k)

            field = self.fields.get(k)
            if field is None:
                if ":" not in k and k[0] != "$":
                    # heuristics to ignore $schemas, $namespaces and custom tags
                    problems += [
                        Diagnostic(
                            _range=key_lookup_node.loc,
                            message=f"Unknown field: {k}",
                            severity=DiagnosticSeverity.Warning)
                    ]

            else:
                inferred_type, type_check_results = infer_type(child_node, field.types, lom_key=lom_key)
                add_to_problems(value_lookup_node.loc, type_check_results, problems)
                inferred_type.parse(
                    node=child_node,
                    value_lookup_node=value_lookup_node,
                    lom_key=lom_key,
                    parent_completer_node=parent_completer_node,
                    completer=completer,
                    problems=problems,
                    requirements=requirements)


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


# ## Use as ##
# import json
# fname = 'schema.json'
# schema = json.load(open(fname, "r"))
# lang_model = {}
# parse_cwl_type(schema, lang_model)
