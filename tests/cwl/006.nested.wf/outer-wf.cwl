class: Workflow
cwlVersion: v1.0
id: outer_wf
label: outer WF
$namespaces:
  sbg: 'https://www.sevenbridges.com/'
inputs:
  - id: input
    type: File?
    'sbg:x': -318
    'sbg:y': -86
  - id: dummy
    type: string?
    'sbg:exposed': true
outputs:
  - id: output
    outputSource:
      - merge/merge_out
    type: File?
    'sbg:x': 148
    'sbg:y': -86
steps:
  - id: inner_wf
    in:
      - id: input
        source: input
      - id: dummy
        source: dummy
    out:
      - id: output
    run: ./inner-wf.cwl
    label: inner WF
    'sbg:x': -136
    'sbg:y': -27
  - id: pass_through
    in:
      - id: input
        source: input
    out:
      - id: output
    run: ./pass-through.cwl
    label: pass-through
    'sbg:x': -142
    'sbg:y': -158
  - id: merge
    in:
      - id: merge_in
        source:
          - pass_through/output
          - inner_wf/output
          - inner_wf_1/output
    out:
      - id: merge_out
    run: ./merge.cwl
    label: merge
    'sbg:x': 22.60113525390625
    'sbg:y': -85
  - id: inner_wf_1
    in:
      - id: input
        source: input
    out:
      - id: output
    run: ./inner-wf.cwl
    label: inner WF
    'sbg:x': -131
    'sbg:y': 106
requirements:
  - class: SubworkflowFeatureRequirement
  - class: MultipleInputFeatureRequirement
