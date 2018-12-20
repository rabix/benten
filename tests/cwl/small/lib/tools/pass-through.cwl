class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  sbg: 'https://www.sevenbridges.com/'
id: pass_through
baseCommand:
  - cat
inputs:
  - id: pt_in1
    type: File?
    inputBinding:
      position: 0
  - id: pt_in2
    type: string?
    inputBinding:
      position: 0
outputs:
  - id: pt_out
    type: File?
    outputBinding:
      glob: '*.txt'
label: pass-through
requirements:
  - class: DockerRequirement
    dockerPull: alpine
stdout: out.txt
