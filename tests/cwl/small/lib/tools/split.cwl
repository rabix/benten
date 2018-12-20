class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  sbg: 'https://www.sevenbridges.com/'
id: split
baseCommand:
  - split
inputs:
  - id: split_in
    type: File?
    inputBinding:
      position: 0
outputs:
  - id: split_out
    type: 'File[]?'
    outputBinding:
      glob: out-*
label: split
arguments:
  - position: 0
    prefix: '-l'
    valueFrom: '1'
  - position: 100
    prefix: ''
    valueFrom: out-
requirements:
  - class: DockerRequirement
    dockerPull: alpine
