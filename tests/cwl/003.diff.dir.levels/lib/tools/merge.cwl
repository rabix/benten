class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  sbg: 'https://www.sevenbridges.com/'
id: merge
baseCommand:
  - cat
inputs:
  - id: merge_in
    type: 'File[]?'
    inputBinding:
      position: 0
outputs:
  - id: merge_out
    type: File?
    outputBinding:
      glob: '*.txt'
label: merge
requirements:
  - class: DockerRequirement
    dockerPull: alpine
stdout: out.txt
