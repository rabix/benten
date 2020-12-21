"""Code to load the CWL specification from JSON and represent it as a
set of types"""

#  Copyright (c) 2019-2020 Seven Bridges. See LICENSE

import json

from .alltypes import *


import logging
logger = logging.getLogger(__name__)


latest_published_cwl_version = "v1.2.0"
process_types = ["CommandLineTool", "ExpressionTool", "Workflow"]


def parse_schema(schema):
    type_dict = {}
    add_formal_primitive_types_to_type_dict(schema, type_dict)
    parse_cwl_type(schema, type_dict)
    clean_up_schema(type_dict)
    return type_dict


def add_formal_primitive_types_to_type_dict(schema, type_dict):
    _primitive_type_definition = next(
        (s for s in schema if s.get("name") == "PrimitiveType"), None)

    for pt in _primitive_type_definition.get("symbols"):
        type_dict[pt] = CWLBaseType(name=pt)


# CWL grows hairy. It needs to be shaved periodically
def clean_up_schema(type_dict):
    if isinstance(type_dict.get("CWLVersion"), CWLEnumType):
        type_dict["CWLVersion"].symbols = [
            symbol
            for symbol in type_dict["CWLVersion"].symbols
            if not symbol.startswith("draft-")
        ]
        type_dict["CWLVersion"].symbols.remove("v1.0.dev4")
        return

    logger.error("No CWLVersion enum in schema")


def parse_cwl_type(schema, lang_model, map_subject_predicate=None, field_name=None):

    # There are no forward references in the schema. Every object is defined the
    # first time it is encountered
    if isinstance(schema, str):
        return lang_model[schema]

    elif isinstance(schema, list):
        return [
            parse_cwl_type(_scheme, lang_model, map_subject_predicate, field_name)
            for _scheme in schema
        ]

    elif schema.get("type") == "array":
        name = field_name
        if map_subject_predicate is None:
            return CWLArrayType(
                name=name,
                allowed_types=parse_cwl_type(schema.get("items"), lang_model))
        else:
            return CWLListOrMapType(
                name=name,
                allowed_types=parse_cwl_type(schema.get("items"), lang_model),
                map_sp=map_subject_predicate)

    elif schema.get("type") == "enum":
        return parse_enum(schema, lang_model)

    elif schema.get("type") == "record":
        return parse_record(schema, lang_model)

    logger.error(f"Unknown schema type {schema.get('type')}: {schema}")


def parse_enum(schema, lang_model):
    enum_name = schema.get("name")

    if enum_name == "Any":
        # This is a special type masquerading as an enum
        lang_model[enum_name] = CWLAnyType(name=schema.get("name"), type_dict=lang_model)
        return lang_model.get(enum_name)

    if enum_name == "Expression":
        # Yet another special type masquerading as an enum
        lang_model[enum_name] = CWLExpressionType(name=schema.get("name"))
        return lang_model.get(enum_name)

    symbols = schema.get("symbols")
    for extends in listify(schema.get("extends")):
        extends = extends.split("#")[1]  # Proper way is to use URIs ...
        if extends in lang_model:
            symbols += lang_model[extends].symbols

    lang_model[enum_name] = CWLEnumType(
        name=schema.get("name"),
        symbols=set(symbols))

    return lang_model.get(enum_name)


def parse_record(schema, lang_model):
    record_name = schema.get("name")
    fields = {}
    for extends in listify(schema.get("extends")):
        extends = extends.split("#")[1]  # Proper way is to use URIs ...
        if extends in lang_model:
            fields.update(**lang_model[extends].fields)

    # It is important to add the still-being-created type to the type dict
    # so as to handle self-references
    lang_model[record_name] = CWLRecordType(
        name=record_name,
        doc=schema.get("doc"),
        fields=fields)

    lang_model[record_name].fields.update(**{
        k: v
        for field in schema.get("fields") for k, v in [parse_field(field, lang_model)]
    })

    lang_model[record_name].init()

    return lang_model.get(record_name)


def listify(items):
    if items is None:
        return []
    elif isinstance(items, list):
        return items
    else:
        return [items]


def parse_field(field, lang_model):

    field_name = field.get("name")
    required = True
    _allowed_types = field.get("type")
    if isinstance(_allowed_types, list) and "null" in _allowed_types:
        required = False
        _allowed_types.remove("null")

    map_subject_predicate = None
    jldp = field.get("jsonldPredicate")
    if isinstance(jldp, dict):
        if "mapSubject" in jldp:
            map_subject_predicate = MapSubjectPredicate(jldp.get("mapSubject"),
                                                        jldp.get("mapPredicate"))

    return field_name, CWLFieldType(
        doc=field.get("doc"),
        required=required,
        allowed_types=parse_cwl_type(
            _allowed_types, lang_model,
            map_subject_predicate=map_subject_predicate,
            field_name=field_name)
    )
