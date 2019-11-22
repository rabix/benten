class: Workflow
cwlVersion: v1.0

inputs:
  in1: File

steps:
  step1:
    run: clt1.cwl
    in:
        in1: in1
    out: [out1]

outputs:
  out1:
    type: string
    outputSource:
      - step1/out1
      - 2
      -

    # Ensures code is proof against ints and Nones in source list
    # Code should flag "2" as invalid input

requirements:
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}
