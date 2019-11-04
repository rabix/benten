class: Workflow
cwlVersion: v1.0

inputs:
  in1: string
  in2: File

steps:
  step1:
    run: clt1.cwl
    in:
      in1:
        source: in2
        valueFrom: $(self.path)
    out: [out1]

outputs:
  out1:
    type: string
    outputSource: step1/out1

requirements:
  StepInputExpressionRequirement: {}
  InlineJavascriptRequirement: {}
