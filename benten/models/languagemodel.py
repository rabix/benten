"""Create completion/validation code from the schema JSON.

For completions we pass a document path to a completion
object.

For particular fields, like for the Workflow `run` step we
create custom completers which we later patch in elsewhere.

For validations we use an allied mechanism where we
traverse the document tree and the completion tree in
parallel, flagging inconsistencies as we go.
"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from typing import Union, Dict
import json
from enum import IntEnum
from abc import abstractmethod

from ..langserver.lspobjects import (mark_problem, DiagnosticSeverity)
from .lineloader import YNone, LAM

import logging
logger = logging.getLogger(__name__)


latest_published_cwl_version = "v1.0"

primitive_types = ['null','string', 'boolean', 'int', 'long']


def load_languagemodel(fname):
    lang_model = {}
    schema = json.load(open(fname, "r"))
    parse_cwl_type(schema, lang_model)
    parse_cwl_type(schema, lang_model)  # Two passes takes care of forward references
    clean_up_model(lang_model)
    return lang_model


# CWL grows hairy. It needs to be shaved periodically
def clean_up_model(lang_model):
    if isinstance(lang_model.get("CWLVersion"), CWLEnum):
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
            return CWLArray(parse_cwl_type(schema.get("items"), lang_model))
        else:
            return CWLListOrMap(parse_cwl_type(schema.get("items"), lang_model), lom_key=lom_key)

    elif schema.get("type") == "enum":
        return parse_enum(schema, lang_model)

    elif schema.get("type") == "record":
        return parse_record(schema, lang_model)

    logger.error(f"Unknown schema type {schema.get('type')}: {schema}")


def parse_enum(schema, lang_model):
    enum_name = schema.get("name")
    if True: # enum_name not in lang_model:
        lang_model[enum_name] = CWLEnum(
            name=schema.get("name"),
            doc=schema.get("doc"),
            symbols=schema.get("symbols"))

    return lang_model.get(enum_name)


def parse_record(schema, lang_model):
    record_name = schema.get("name")
    if True: # record_name not in lang_model:
        lang_model[record_name] = CWLRecord(
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

    return field_name, CWLField(
        doc=field.get("doc"),
        required=required,
        allowed_types=parse_cwl_type(_allowed_types, lang_model, lom_key=lom_key)
    )


def infer_cwl_version(doc: dict):
    v = doc.get("cwlVersion")
    if not isinstance(v, str):
        v = latest_published_cwl_version
    return v


def select_language_model(doc: dict, lang_models: dict):
    cwl_v = infer_cwl_version(doc)
    lm = lang_models.get(cwl_v)
    if lm is None:
        logger.error(f"No language model for cwl version {cwl_v}. Using {latest_published_cwl_version}")
        lm = lang_models.get(latest_published_cwl_version)

    return lm


def infer_model_from_type(doc: dict, lang_model: dict):
    if "class" in doc:
        return lang_model.get(doc.get("class"))

    if "type" in doc:
        return lang_model.get(doc.get("type"))


class ValidationResult(IntEnum):
    Valid = 1           # Everything checks out
    InvalidValue = 2    # We can identify the value as of this type, but it's value is wrong
    InvalidType = 3     # We can't identify the node as being of this type


class CWLBaseType:

    @abstractmethod
    def validate(self, node, problems, requirements=None):
        pass


class CWLEnum(CWLBaseType):

    def __init__(self, name: str, doc: str, symbols: list):
        self.name = name
        self.doc = doc
        self.symbols = symbols

    def __str__(self):
        return str(self.symbols)

    def __repr__(self):
        return str(self)

    # def is_the_type_for(self, node):
    #     return isinstance(node, str)

    def validate(self, node, problems, requirements=None):

        if not isinstance(node, str):
            return ValidationResult.InvalidType

        if node not in self.symbols:
            problems += [mark_problem(f"Expecting one of {self.symbols}",
                                      DiagnosticSeverity.Error, node)]
            return ValidationResult.InvalidValue
        else:
            return ValidationResult.Valid


class CWLArray(CWLBaseType):

    def __init__(self, allowed_types):
        self.name = "list"
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types

    def __str__(self):
        return str(self.types)

    def __repr__(self):
        return str(self)

    def validate(self, node, problems, requirements=None):

        if not isinstance(node, list):
            return ValidationResult.InvalidType

        for v in node:
            _validate(v, self.types, problems, requirements)

        return ValidationResult.Valid


class CWLListOrMap(CWLBaseType):

    def __init__(self, allowed_types, lom_key):
        self.name = "list/map"
        self.lom_key = lom_key
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types

    def validate(self, doc_node, problems, requirements=None):
        if isinstance(doc_node, list):
            for v in doc_node:
                _validate(v, self.types, problems, requirements)
            return ValidationResult.Valid

        elif isinstance(doc_node, dict):
            for v in doc_node.values():
                _validate(v, self.types, problems, requirements, lom_key=self.lom_key)
            return ValidationResult.Valid

        else:
            return ValidationResult.InvalidType


class CWLRecord(CWLBaseType):

    def __init__(self, name: str, doc: str, fields: Dict[str, 'CWLField']):
        self.name = name
        self.doc = doc
        self.fields = fields
        self.required_fields = set((k for k, v in self.fields.items() if v.required))

    def __str__(self):
        return f"{self.name}: {str(self.fields)}"

    def __repr__(self):
        return str(self)

    def validate(self, doc_node, problems, requirements=None, lom_key: LomKey=None):

        required_fields = self.required_fields - {lom_key.subject if lom_key else None}

        # We allow users a shortcut where a type with only one req field
        # can be expressed as a string rep just that req field
        if isinstance(doc_node, str):
            if lom_key is not None:
                if lom_key.predicate in self.fields and len(required_fields) <= 1:
                    return ValidationResult.Valid
            else:
                problems += [
                    mark_problem(f"Tried type {self.name}: Got string",
                                 DiagnosticSeverity.Error, doc_node)]
                return ValidationResult.InvalidType

        fields_present = set(doc_node.keys())
        missing_fields = required_fields - fields_present
        if len(missing_fields):
            for f in missing_fields:
                problems += [
                    mark_problem(f"Tried type {self.name}: Missing required field: {f}",
                                 DiagnosticSeverity.Error, doc_node)]
            return ValidationResult.InvalidType

        # Good use case for key coordinates too
        for k, child_node in doc_node.items():
            field = self.fields.get(k)
            if field is None:
                if ":" not in k and k[0] != "$":
                    # heuristics to ignore $schemas, $namespaces and custom tags
                    problems += [mark_problem(f"Unknown field: {k}",
                                              DiagnosticSeverity.Warning, child_node)]
            else:
                field.validate(child_node, problems, requirements)

        return ValidationResult.Valid


class CWLField(CWLBaseType):

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

    def validate(self, doc_node, problems, requirements=None):
        return _validate(doc_node, self.types, problems, requirements)


class TypeCheckResult:

    def __init__(self, type_tested: str):
        self.type_tested = type_tested
        self.check_result: ValidationResult = None
        self.problems = []


def _validate(doc_node, allowed_types, problems, requirements=None, lom_key=None):

    type_check_results = []

    for _type in allowed_types:
        if _type == 'null':
            if isinstance(doc_node, YNone):
                return ValidationResult.Valid
            else:
                continue

        # For now, don't closely validate these base types
        if _type in ['string', 'boolean', 'int', 'long']:
            if isinstance(doc_node, str):
                return ValidationResult.Valid
            else:
                continue

        this_type = TypeCheckResult(_type.name)
        if isinstance(_type, CWLRecord) and lom_key is not None:
            this_type.check_result = _type.validate(doc_node, this_type.problems, requirements, lom_key=lom_key)
        else:
            this_type.check_result = _type.validate(doc_node, this_type.problems, requirements)

        if this_type.check_result == ValidationResult.Valid:
            problems += this_type.problems
            return ValidationResult.Valid

        type_check_results += [this_type]

    else:
        for check_result in type_check_results:
            problems += check_result.problems
        return ValidationResult.InvalidType


# ## Use as ##
# import json
# fname = 'schema.json'
# schema = json.load(open(fname, "r"))
# lang_model = {}
# parse_cwl_type(schema, lang_model)
