class: Workflow
cwlVersion: v1.2.0-dev1

inputs:
  in1: string
  in2: File

steps:
  step1:
    run: clt1.cwl
    when: $(inputs.new_input)
    in:
      new_input: in1
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
