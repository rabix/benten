# Document model

When we load the CWL document we build a model of it to help with
1. Validation
2. Cursor location 
3. Information on hover
4. Auto-completion

## Validation

At each document element we need to guess what kind of CWL type it is,
and flag any validation errors based on mis-matched types, missing
fields etc.

## Extra validations

Some validations depend on the larger context of the workflow:
1. Do linked workflows exist? 
2. Are the port assignments to/from a step + step tool valid
3. Are there JS expressions, is InlineJavascript requirement present,
   and what do the expressions evaluate to?


## Cursor location

Given a line and column we need to return the document node this covers.
This information is used for hover information and auto-completion

## Hover

Given where the cursor is in the document yield documentation for the
given node type.


## Auto-completion

Auto-completion takes care of suggesting key and value strings based on
what element the cursor is in.


## Extra completions

These are completions (usually for free form strings) that depend on the
larger context of the workflow. There are two kind of custom completion
that are offered

1. `run` field completion. This gives us an inline file picker that
   allows us to select tool/workflow files for the `run` field
2. port completion. This suggests port names for `source` and
   `outputSource` fields based on the available, legal source ports from
   other steps


# Cursor context for completions

Since a YAML document is a tree whose leaves are strings (or numbers) a 
cursor can have the following states

## Over a Key
Offer key completion based on the enclosing node. If the node type has
not been inferred, the keys will be a union of keys taken from all possible 
types.

## Over a value
For values that can take record types we offer completions of all possible
keys. For extra completions (all for string fields) a special completer is 
invoked.

## In between nodes

```
IF block style node and on empty line

    Enclosing node is an ancestor of the parent node of the previous key/value
    Ancestor is computed based on the indent level of the cursor

ELSE

    Enclosing node is that of previous key/value

Offer key completions for the enclosing node  
```

# Coordinates

A YAML document is structured as a tree with leaf nodes being scalar
elements like strings, ints, floats etc. `ruamel.yaml` gives us the 
start locations for all elements. We can infer the end location of keys 
from the length of the string. We can do the same for number
values and single line strings. For multiline strings the inference is a bit
more tricky.


# CWL language model

The CWL specification can be exported into a JSON format using the Schema
Salad tool. 

```
schema-salad-tool --print-avro ~/path/to/cwl/schemas/CommonWorkflowLanguage.yml > schema.json
``` 

The JSON format describes CWL in terms of nested types. Types are mostly record 
types which are described with a dict whose keys are the names of the fields and 
the values are CWL types. An interesting wrinkles is that a CWL type may be
described after it is first declared (used), requiring a two pass parse to 
create the language model.


# CWL type inference

Each node in a CWL document has to match a type. Given a document node it's type
is inferred as follows:

```
IF there is only one type

    Return this as the type

ELSE 

    FOR EACH type in type list

        IF type is a perfect match

            Return this as the type

        ELSE

            Score this type by how many fields match.

    IF Score is greater than zero

        Return the type with maximum score

    ELSE

        Return unknown type
```

# Data structure

## Requirements

- We need an efficient structure to locate if a cursor is over a key, value or
  in-between and to locate which node that key/value/space belongs to
- We need to know which node a key/value is in
- We need to know if a node is block or flow style
- We need to know the parent of a node
- We need to know the indent level of a block level node
- We need to figure out how to find the end of a multi-line string

## Design

We chose to satisfy these requirements using an sorted list of location markers.
Each marker indicates the start and stop of keys and values. Key markers are
linked to enclosing completer objects. Value markers are only needed for leaf
nodes (nodes that are only str type) and usually point to custom completer 
objects.

Completer objects are created during document validation and are defined in
the language model. They typically yield enum values or key values based on the
fields for the CWL object. 


# Parsing the document

For the first version of the algorithm we allow a strong coupling between the
language model


The document tree is traversed depth first. Once the type of a node is inferred
if the type can have descendants, the descendants of the node are recursively
processed. As the document is parsed, any validation warnings and errors are 
added to a list.


# Limitations

1. For flow style we can't detect when the cursor is outside the curly brackets
   and will offer completions as if the cursor is within that enclosing node