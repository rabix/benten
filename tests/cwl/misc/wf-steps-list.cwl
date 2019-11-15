class: Workflow
cwlVersion: v1.0

inputs:
  in1: string

steps:
  - id: step1:
    run: clt1.cwl
    in:
      in1: in2
    out: [out1]

  - # id: step2:  # -> missing id! Benten should not crash, but should warn
    run: clt1.cwl
    in:
      in1: in2
    out: [out1]

outputs:
  out1:
    type: string
    outputSource: step1/out1
