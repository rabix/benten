# This test is somewhat brittle because it assumes the
# existence of this repository on github. If github
# disappears, or this repository is no longer hosted there
# the CWL for this test will have to be updated.

cwlVersion: v1.0
class: Workflow

inputs:
  in1: string

steps:
  step1:
    run: https://raw.githubusercontent.com/denbi/denbi-benten/4223a4/tests/cwl/misc/clt1.cwl
    in:
      in1: in1
    out: [out1]
      
  step2:
    run: https://raw.githubusercontent.com/denbi/denbi-benten/5223a4/tests/cwl/misc/clt1.cwl
    in:
      in1: in1
    out: [out1]


outputs:
  out1:
    type: string
    outputSource: [step1/out1, step2/out1]
