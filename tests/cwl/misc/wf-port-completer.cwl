class: Workflow
cwlVersion: v1.0

inputs:
  in1: string

steps:
  - id: step1
    run: clt1.cwl
    in:
       in1: in1
    out: [out1]

  - id: step2
    run: clt1.cwl
    in:
      in1: step1/out1
    out: [out1]

outputs:
  out1:
    type: string[]
    outputSource:
      - step1/out1
      - in1
