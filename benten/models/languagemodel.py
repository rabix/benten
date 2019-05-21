"""Create completion/validation code from the schema JSON.

For completions we pass a document path to a completion
object.

For particular fields, like for the Workflow `run` step we
create custom completers which we later patch in elsewhere.

For validations we use an allied mechanism where we
traverse the document tree and the completion tree in
parallel, flagging inconsistencies as we go.
"""

#  Copyright (c) 2019 Seven Bridges. Some rights reserved.

from typing import Union, Dict
import json


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


class CWLType:

    def __init__(self, name: str, doc: str, fields: Dict[str, CWLField]):
        self.name = name
        self.doc = doc
        self.fields = fields

    def __str__(self):
        return f"{self.name}: {str(self.fields)}"

    def __repr__(self):
        return str(self)


class CWLEnum:

    def __init__(self, name: str, doc: str, symbols: list):
        self.name = name
        self.doc = doc
        self.symbols = symbols

    def __str__(self):
        return str(self.symbols)

    def __repr__(self):
        return str(self)


class CWLTypeArray:

    def __init__(self, allowed_types):
        self.types = allowed_types

    def __str__(self):
        return str(self.types)

    def __repr__(self):
        return str(self)


def parse_cwl_type(schema, completers):

    if isinstance(schema, str):
        if schema not in completers:
            completers[schema] = schema
        return completers.get(schema)

    elif isinstance(schema, list):
        return [
            parse_cwl_type(_scheme, completers)
            for _scheme in schema
        ]

    elif schema.get("type") == "array":
        return CWLTypeArray(parse_cwl_type(schema.get("items"), completers))

    elif schema.get("type") == "enum":
        return parse_enum(schema, completers)

    elif schema.get("type") == "record":
        return parse_record(schema, completers)


def parse_enum(schema, completers):
    enum_name = schema.get("name")
    if enum_name not in completers:
        completers[enum_name] = CWLEnum(
            name=schema.get("name"),
            doc=schema.get("doc"),
            symbols=schema.get("symbols")
        )
    return completers.get(enum_name)


def parse_record(schema, completers):
    record_name = schema.get("name")
    if record_name not in completers:
        completers[record_name] = CWLType(
            name=record_name,
            doc=schema.get("doc"),
            fields={
                k: v
                for field in schema.get("fields") for k, v in [parse_field(field, completers)]
            }
        )

    return completers.get(record_name)


def parse_field(field, completers):

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
        doc=field.get("name"),
        required=required,
        lom_key=lom_key,
        allowed_types=parse_cwl_type(field.get("type"), completers)
    )

# ## Use as ##
#
# fname = 'schema.json'
# schema = json.load(open(fname, "r"))
# completers = {}
# parse_cwl_type(schema, completers)
