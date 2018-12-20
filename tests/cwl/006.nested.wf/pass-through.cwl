class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  sbg: 'https://www.sevenbridges.com/'
id: pass_through
baseCommand:
  - cat
inputs:
  - id: input
    type: File?
    inputBinding:
      position: 0
  - id: dummy
    type: string?
    inputBinding:
      position: 0
outputs:
  - id: output
    type: File?
    outputBinding:
      glob: '*.txt'
label: pass-through
requirements:
  - class: DockerRequirement
    dockerPull: alpine
stdout: out.txt
