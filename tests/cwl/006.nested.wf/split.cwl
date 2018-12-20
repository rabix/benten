class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  sbg: 'https://www.sevenbridges.com/'
id: split
baseCommand:
  - split
inputs:
  - id: input
    type: File?
    inputBinding:
      position: 0
outputs:
  - id: output
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
