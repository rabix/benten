# cwltoil workflows/scatter.cwl --val 4 


class: Workflow
cwlVersion: v1.0
inputs:
  val: int

steps: 

  step1:
    in:
      in1: val
    run: ../tools/listify.cwl
    out: [out1]

  step2:
    blah: 34
    in:
      in1: step1/out1
    scatter: [in1]
    run: ../tools/foo.cwl
    out: [out1]
    
  step3:
    in:
      in1: step1/out1
    scatter: [in1]
    run: ../tools/bar.cwl
    out: [out1]

outputs: 
  out1:
    type: string[]
    outputSource:
      - step2/out1
      - step3/out1
    linkMerge: merge_flattened  # Omitting will give validation error

requirements: 
  ScatterFeatureRequirement: {}
  InlineJavascriptRequirement: {}
  MultipleInputFeatureRequirement: {}