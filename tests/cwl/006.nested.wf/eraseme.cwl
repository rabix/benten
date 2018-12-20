class: Workflow
cwlVersion: v1.0
id: inner_wf
label: inner WF
$namespaces:
  sbg: https://www.sevenbridges.com/
inputs:
- id: input
  type: File?
  sbg:x: -429.57598876953125
  sbg:y: 2
- id: dummy
  type: string?
  sbg:exposed: true
outputs:
- id: output
  outputSource:
  - merge/output
  type: File?
  sbg:x: 140
  sbg:y: 4
steps:
- id: split
  in:
  - id: input
    source: input
  out:
  - id: output
  run: ./split.cwl
  label: split
  sbg:x: -279.3984375
  sbg:y: 3
- id: pass_through
  in:
  - id: input
    source: split/output
  - id: dummy
    source: dummy
  out:
  - id: output
  run: ./pass-through.cwl
  label: pass-through
  scatter:
  - input
  scatterMethod: dotproduct
  sbg:x: -134
  sbg:y: 3
- id: merge
  in:
  - id: input
    source:
    - pass_through/output
  out:
  - id: output
  run: ./merge.cwl
  label: merge
  sbg:x: 17
  sbg:y: 3
- id: bwa_mem_0_7_17
  label: bwa_mem_0_7_17
  in: []
  out: []
  run: ../../../../../composer-bugs/github-417/bwa.cwl
requirements:
- class: ScatterFeatureRequirement


