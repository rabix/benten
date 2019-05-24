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

from ..langserver.lspobjects import (mark_problem, DiagnosticSeverity)

import logging
logger = logging.getLogger(__name__)


latest_published_cwl_version = "v1.0"


def infer_cwl_version(doc: dict):
    return doc.get("cwlVersion", latest_published_cwl_version)


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


class CWLField:

    def __init__(self, doc: str, required: bool, lom_key: Union[None, str], allowed_types: list):
        self.doc = doc
        self.required = required
        self.lom_key = lom_key
        self.types = allowed_types

    def __str__(self):
        return str(self.types)

    def __repr__(self):
        return str(self)

    def validate(self, doc_node, problems, requirements=None):



        pass


class CWLType:

    def __init__(self, name: str, doc: str, fields: Dict[str, CWLField]):
        self.name = name
        self.doc = doc
        self.fields = fields

    def __str__(self):
        return f"{self.name}: {str(self.fields)}"

    def __repr__(self):
        return str(self)

    def validate(self, doc_node, problems, requirements=None):
        required_fields = set((k for k, v in self.fields.items() if v.required))
        fields_present = set(doc_node.keys())
        missing_required_fields = required_fields - fields_present

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
                field.validate(child_node, problems)


class CWLEnum:

    def __init__(self, name: str, doc: str, symbols: list):
        self.name = name
        self.doc = doc
        self.symbols = symbols

    def __str__(self):
        return str(self.symbols)

    def __repr__(self):
        return str(self)

    def validate(self, doc_node, problems, requirements=None):
        if not isinstance(doc_node, str):
            problems += [mark_problem(f"This is an enum. Should be a string like : {self.symbols}",
                                      DiagnosticSeverity.Error, doc_node)]
        elif doc_node not in self.symbols:
            problems += [mark_problem(f"Expecting one of {self.symbols}",
                                      DiagnosticSeverity.Error, doc_node)]


class CWLTypeArray:

    def __init__(self, allowed_types):
        self.types = allowed_types

    def __str__(self):
        return str(self.types)

    def __repr__(self):
        return str(self)

    def validate(self, doc_node, problems, requirements=None):
        pass


def parse_cwl_type(schema, lang_model):

    if isinstance(schema, str):
        if schema not in lang_model:
            lang_model[schema] = schema
        return lang_model.get(schema)

    elif isinstance(schema, list):
        return [
            parse_cwl_type(_scheme, lang_model)
            for _scheme in schema
        ]

    elif schema.get("type") == "array":
        return CWLTypeArray(parse_cwl_type(schema.get("items"), lang_model))

    elif schema.get("type") == "enum":
        return parse_enum(schema, lang_model)

    elif schema.get("type") == "record":
        return parse_record(schema, lang_model)

    logger.error(f"Unknown schema type {schema.get('type')}: {schema}")


def parse_enum(schema, lang_model):
    enum_name = schema.get("name")
    if enum_name not in lang_model:
        lang_model[enum_name] = CWLEnum(
            name=schema.get("name"),
            doc=schema.get("doc"),
            symbols=schema.get("symbols")
        )
    return lang_model.get(enum_name)


def parse_record(schema, lang_model):
    record_name = schema.get("name")
    if record_name not in lang_model:
        lang_model[record_name] = CWLType(
            name=record_name,
            doc=schema.get("doc"),
            fields={
                k: v
                for field in schema.get("fields") for k, v in [parse_field(field, lang_model)]
            }
        )

    return lang_model.get(record_name)


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
        allowed_types=parse_cwl_type(_allowed_types, lang_model)
    )


def load_languagemodel(fname):
    lang_model = {}
    schema = json.load(open(fname, "r"))
    parse_cwl_type(schema, lang_model)
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
    else:
        logger.error("No CWLVersion enum in schema")


# ## Use as ##
# import json
# fname = 'schema.json'
# schema = json.load(open(fname, "r"))
# lang_model = {}
# parse_cwl_type(schema, lang_model)
