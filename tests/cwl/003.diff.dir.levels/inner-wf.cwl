class: Workflow
cwlVersion: v1.0
id: inner_wf
label: Inner WF
$namespaces:
  sbg: 'https://www.sevenbridges.com/'
inputs:
  - id: inner_in
    type: File?
    'sbg:x': -401.4876708984375
    'sbg:y': -1
outputs:
  - id: merge_out
    outputSource:
      - merge/merge_out
    type: File?
    'sbg:x': 179
    'sbg:y': 5
steps:
  - id: split
    in:
      - id: split_in
        source: inner_in
    out:
      - id: split_out
    run: lib/tools/split.cwl
    label: split
    'sbg:x': -263
    'sbg:y': 0
  - id: pass_through
    in:
      - id: pt_in1
        source: split/split_out
    out:
      - id: pt_out
    run: lib/tools/pass-through.cwl
    label: pass-through
    scatter:
      - pt_in1
    scatterMethod: dotproduct
    'sbg:x': -119
    'sbg:y': 2
  - id: merge
    in:
      - id: merge_in
        source:
          - pass_through/pt_out
    out:
      - id: merge_out
    run: lib/tools/merge.cwl
    label: merge
    'sbg:x': 31
    'sbg:y': 5
requirements:
  - class: ScatterFeatureRequirement
