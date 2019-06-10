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
    def is_the_type_for(self, node):
        pass

    @abstractmethod
    def validate(self, node, problems, requirements=None):
        pass


# This is a trick to allow us to fill in the real type with one
# pass of the spec. When we find a forward reference to a type in the
# spec JSON we create CWLTypeWrapper object as a shell which we can
# fill in later. If this is the first time we've encountered this type
# We create it all at the same time
class CWLTypeWrapper(CWLBaseType):

    def __init__(self, the_type: CWLBaseType):
        self._underlying_type: CWLBaseType = the_type

    def get_type(self):
        return self._underlying_type

    def set_type(self, the_type: CWLBaseType):
        self._underlying_type = the_type

    def is_the_type_for(self, node):
        return self._underlying_type.is_the_type_for(node)

    def validate(self, node, problems, requirements=None):
        return self._underlying_type.validate(node, problems, requirements)


class CWLEnum(CWLBaseType):

    def __init__(self, name: str, doc: str, symbols: list):
        self.name = name
        self.doc = doc
        self.symbols = symbols

    def __str__(self):
        return str(self.symbols)

    def __repr__(self):
        return str(self)

    def is_the_type_for(self, node):
        return isinstance(node, str)

    def validate(self, node, problems, requirements=None):
        if node not in self.symbols:
            problems += [mark_problem(f"Expecting one of {self.symbols}",
                                      DiagnosticSeverity.Error, node)]
            return ValidationResult.InvalidValue
        else:
            return ValidationResult.Valid


class CWLArray(CWLBaseType):

    def __init__(self, allowed_types, lom_key):
        self.lom_key = lom_key
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types

    def __str__(self):
        return str(self.types)

    def __repr__(self):
        return str(self)

    def is_the_type_for(self, node):
        if self.lom_key is not None:
            valid_types = (list, dict)
        else:
            valid_types = (list,)
        return isinstance(node, valid_types)

    def validate(self, node, problems, requirements=None):
        if isinstance(node, list):
            values = node
        else:
            values = node.values()

        for v in values:
            _validate(v, self.types, problems, requirements)


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

    def is_the_type_for(self, node):
        if isinstance(node, dict):
            if node.get("class") == self.name:
                return True
            elif node.get("type") == self.name:
                return True

            mf = self.missing_required_fields(node)
            if mf is None:
                return False

            if len(mf) == 0:
                return True
        else:
            if len(self.required_fields) == 1 and isinstance(node, str):
                # We allow users a shortcut where a type with only one req field
                # can be expressed as a string rep just that req field
                return True
            else:
                return False

    def missing_required_fields(self, node):
        if isinstance(node, dict):
            fields_present = set(node.keys())
            return self.required_fields - fields_present
        else:
            return None

    def validate(self, doc_node, problems, requirements=None):
        if isinstance(doc_node, str):
            return True

        fields_present = set(doc_node.keys())
        missing_required_fields = self.required_fields - fields_present

        for f in missing_required_fields:
            problems += [mark_problem(f"Missing required field: {f}", DiagnosticSeverity.Error)]

        # Good use case for key coordinates too
        for k, child_node in doc_node.items():
            field = self.fields.get(k)
            if field is None:
                if ":" not in k and k[0] != "$":
                    # heuristics to ignore $schemas, $namespaces and custom tags
                    problems += [mark_problem(f"Unknown field: {k}", DiagnosticSeverity.Warning, child_node)]
            else:
                field.validate(child_node, problems, requirements)


class CWLField:

    def __init__(self, doc: str, required: bool, lom_key: Union[None, str], allowed_types: list):
        self.doc = doc
        self.required = required
        self.lom_key = lom_key
        if not isinstance(allowed_types, list):
            allowed_types = [allowed_types]
        self.types = allowed_types

    def __str__(self):
        return str(self.types)

    def __repr__(self):
        return str(self)

    def validate(self, doc_node, problems, requirements=None):
        return _validate(doc_node, self.types, problems, requirements)


def _validate(doc_node, allowed_types, problems, requirements=None):
    for _type in allowed_types:
        if _type == 'null':
            if isinstance(doc_node, YNone):
                return True
            else:
                continue

        # For now, don't closely validate these base types
        if _type in ['string', 'boolean', 'int', 'long']:
            if isinstance(doc_node, str):
                return True
            else:
                continue

        if _type.is_the_type_for(doc_node):
            return _type.validate(doc_node, problems, requirements)

    else:
        # problems += [mark_problem(f"Mismatched type", DiagnosticSeverity.Warning, doc_node)]
        return False


def parse_cwl_type(schema, lang_model, lom_key=None):

    if isinstance(schema, str):
        if schema not in lang_model:
            if schema not in primitive_types:
                lang_model[schema] = CWLTypeWrapper(the_type=None)
            else:
                lang_model[schema] = schema
        return lang_model.get(schema)

    elif isinstance(schema, list):
        return [
            parse_cwl_type(_scheme, lang_model, lom_key)
            for _scheme in schema
        ]

    elif schema.get("type") == "array":
        return CWLTypeWrapper(
            the_type=CWLArray(parse_cwl_type(schema.get("items"), lang_model, lom_key), lom_key=lom_key))

    elif schema.get("type") == "enum":
        return parse_enum(schema, lang_model)

    elif schema.get("type") == "record":
        return parse_record(schema, lang_model)

    logger.error(f"Unknown schema type {schema.get('type')}: {schema}")


def parse_enum(schema, lang_model):
    enum_name = schema.get("name")
    if enum_name not in lang_model:
        lang_model[enum_name] = CWLTypeWrapper(the_type=None)

    wrapper = lang_model.get(enum_name)
    wrapper.set_type(
        the_type=CWLEnum(
            name=schema.get("name"),
            doc=schema.get("doc"),
            symbols=schema.get("symbols")))

    return wrapper


def parse_record(schema, lang_model):
    record_name = schema.get("name")
    if record_name not in lang_model:
        lang_model[record_name] = CWLTypeWrapper(the_type=None)

    wrapper = lang_model.get(record_name)
    wrapper.set_type(
        the_type=CWLRecord(
            name=record_name,
            doc=schema.get("doc"),
            fields={
                k: v
                for field in schema.get("fields") for k, v in [parse_field(field, lang_model)]
            }))

    return wrapper


def parse_field(field, lang_model):

    field_name = field.get("name")
    required = True
    _allowed_types = field.get("type")
    if isinstance(_allowed_types, list) and "null" in _allowed_types:
        required = False

    lom_key = None
    jldp = field.get("jsonldPredicate")
    if isinstance(jldp, dict):
        lom_key = jldp.get("mapSubject")

    return field_name, CWLField(
        doc=field.get("doc"),
        required=required,
        lom_key=lom_key,
        allowed_types=parse_cwl_type(_allowed_types, lang_model, lom_key=lom_key)
    )


def load_languagemodel(fname):
    lang_model = {}
    schema = json.load(open(fname, "r"))
    parse_cwl_type(schema, lang_model)
    clean_up_model(lang_model)
    return lang_model


# CWL grows hairy. It needs to be shaved periodically
def clean_up_model(lang_model):
    if isinstance(lang_model.get("CWLVersion"), CWLTypeWrapper):
        if isinstance(lang_model["CWLVersion"].get_type(), CWLEnum):
            lang_model["CWLVersion"].symbols = [
                symbol
                for symbol in lang_model["CWLVersion"].get_type().symbols
                if not symbol.startswith("draft-")
            ]
            lang_model["CWLVersion"].symbols.remove("v1.0.dev4")
            return

    logger.error("No CWLVersion enum in schema")


# ## Use as ##
# import json
# fname = 'schema.json'
# schema = json.load(open(fname, "r"))
# lang_model = {}
# parse_cwl_type(schema, lang_model)
