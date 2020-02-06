class: CommandLineTool
cwlVersion: v1.0
inputs:
  in1: 
    type: paired_end_record.yml#paired_end_options

requirements:
  - class: ResourceRequirement
    coresMin: 1
  - class: InlineJavascriptRequirement
  - class: SchemaDefRequirement
    types:
      - $import: paired_end_record.yml
