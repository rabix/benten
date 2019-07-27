# Main steps executed by the server

1. The CWL schema (in JSON format) is loaded to create a library
   of _type templates_. Each version of the CWL specification has
   a different schema. (This only has to be done at startup)
2. The CWL document is parsed, validation issues are listed and a
   lookup table is created mapping each node to a relevant code
   intelligence object. Code intelligence is computed as lazily
   as possible - the actual completions are computed only when
   asked for. In many cases, however, most of the required 
   computations have already been done during validation. 
3. If the document is identified as a process object top level
   symbols are extracted
4. If the document is a workflow steps are added to the symbols and
   the workflow connectivity is analyzed
5. When a hover, goto definition or completion request is received
   the relevant code_intelligence object is pulled up and the code intelligence
   action is invoked

## Document parsing
1. The CWL document is traversed depth first. 
2. The CWL type of each node is inferred based on the type of the 
   node and the CWL types allowed in that context. 
3. Once a CWL type is inferred any child nodes are recursively 
   analyzed based on the allowed types in the fields of the 
   inferred node. 
4. As we traverse the document any issues are flagged. 
5. A table is created with lookup tokens that map document 
   locations (elements) to relevant code_intelligence objects.

# Completions

## Key completion for any Record type

```
fi -> (complete with names of fields)
```
or

```
fi -> (complete with names of fields)
field1: value1
field2: value2
```
or

```
field1: value1
field2: value2
fi -> (complete with names of fields)
```

## Completion for particular list/map types 

List/Map types are collections of record types where
one field is marked as a key_field and one as a value_field.
Either the key field, or the value field or both may have
special completions.

### Requirements

#### Expressed as list:

key completions - class  
value completion for class - type names  

Once a type has been established, completion for that follows
the given type (i.e. just like a record) 

#### Expressed as map

key completions - type names
value completions - follows completion for the given type


### in field of step

#### Expressed as list

key completions - same as that for enclosing type which is
WFStepInput

value completion for id: port names
value completion for source: connection names not of this step

#### Expressed as map

key completions: port names
value completion: connection names not of this step
value completion for source: connection names not of this step

### out field of workflow

#### Expressed as list

value completion for outputSource: connection names

#### Expressed as map

value completion: connection names
value completion for outputSource: connection names

## Completions for `out` field of step

List of sub process outputs not yet used. The collection is
a list and so the completer should apply to any item


## Completions for linked files
This is a file picker. This also supports goto definition


## Completions for enums
These are value field completions and are just the list of symbols




requirements
```
requirements:
  - class: SomeRequirement ->(RequirementCompleter)
  - class: SomeOtherRequirement ->(RequirementCompleter)

requirements:
  SomeRequirement ->(RequirementCompleter): {}
  SomeOtherRequirement ->(RequirementCompleter): {}
```

Step inputs
```
in:
  - id: input1 ->(WFStepInputs)
    source: stepX/portY ->(WFPortCompleter)
  - id: input2 ->(WFStepInputs)
    source: stepX/portY ->(WFPortCompleter)

in:
  input1 ->(WFStepInputs): stepX/portY ->(WFPortCompleter)
  input2 ->(WFStepInputs): stepX/portY ->(WFPortCompleter)

in:
  input1 ->(WFStepInputs): 
    - stepX/portY ->(WFPortCompleter)
    - stepW/portZ ->(WFPortCompleter)

  input2 ->(WFStepInputs): stepX/portY ->(WFPortCompleter)
```

Workflow outputs
```
outputs:
  - id: output1
    outputSource: stepX/portY ->(WFPortCompleter)
  - id: output2
    outputSource: stepX/portY ->(WFPortCompleter)
  - id: output3
    outputSource: 
      - stepX/portY ->(WFPortCompleter)
      - stepW/portZ ->(WFPortCompleter)


outputs:
  output1: stepX/portY ->(WFPortCompleter)
  output2: stepX/portY ->(WFPortCompleter)
```


## Keys

Key completions are always based on the parent (enclosing node). For
record types they are simply the names of the record's fields. For
arrays nothing special is done. For Map/List types there are no
completions except in the  following interesting exceptions 
when they are expressed as map

- Requirements: Key completions are the type names
- WorkflowStepInputs: Key completions are names of the available step inputs

## Values

Values always have interesting completions. They have to be inferred from
the field they are in and almost always require special completers

- Enums: list of accepted symbols
- LinkedFiles: File picker for `run` and `$include` fields
- class (requirements): allowed type names
- value for map form of WorkflowStepInput: any of the ports
- 'source' (WorkflowStepInput): any of the ports
- 'outputSource (WorkflowOutput): any of the ports
- out (WorkflowStep): CWLArray 


