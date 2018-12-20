class: Workflow
cwlVersion: v1.0
id: outer_wf
label: outer-wf
$namespaces:
  sbg: 'https://www.sevenbridges.com/'
inputs:
  - id: wf_in
    type: File?
    'sbg:x': -259
    'sbg:y': -53
  - id: wf_in2
    type: File?
    'sbg:x': -307
    'sbg:y': -281
outputs:
  - id: wf_out
    outputSource:
      - merge/merge_out
      - pass_through/pt_out
    type:
      - 'null'
      - File
      - type: array
        items: File
    'sbg:x': 313.60113525390625
    'sbg:y': -54
  - id: wf_out2
    outputSource:
      - wf_in2
    type: File?
    'sbg:x': 175
    'sbg:y': -281
steps:
  - id: pass_through
    in:
      - id: pt_in1
        source: wf_in
    out:
      - id: pt_out
    run: ../tools/pass-through.cwl
    label: pass-through
    'sbg:x': -64
    'sbg:y': -193
  - id: merge
    in:
      - id: merge_in
        source:
          - pass_through/pt_out
          - inner_wf/merge_out
          - inner_wf_1/merge_out
    out:
      - id: merge_out
    run: ../tools/merge.cwl
    label: merge
    'sbg:x': 165.60113525390625
    'sbg:y': -53
  - id: inner_wf
    in:
      - id: inner_in
        source: wf_in
    out:
      - id: merge_out
    run: ../../inner-wf.cwl
    label: Inner WF
    'sbg:x': -58
    'sbg:y': -53
  - id: inner_wf_1
    in:
      - id: inner_in
        source: wf_in
    out:
      - id: merge_out
    run: ../../inner-wf.cwl
    label: Inner WF
    'sbg:x': -56
    'sbg:y': 85
requirements:
  - class: SubworkflowFeatureRequirement
  - class: MultipleInputFeatureRequirement
