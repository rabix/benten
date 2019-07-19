# Main steps executed by the server

1. The CWL schema (in JSON format) is loaded to create a library
   of _type templates_. Each version of the CWL specification has
   a different schema. (This only has to be done at startup)
2. The CWL document is parsed, validation issues are listed and a
   lookup table is created mapping each node to a relevant code
   intelligence object.
3. If the document is identified as a process object top level
   symbols are extracted
4. If the document is a workflow steps are added to the symbols and
   the workflow connectivity is analyzed
5. When a hover, goto definition or completion request is received
   the relevant completer object is pulled up and the code intelligence
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
   locations (elements) to relevant completer objects.

# Completions

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


## Examples

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
