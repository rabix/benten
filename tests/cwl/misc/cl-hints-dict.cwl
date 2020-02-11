class: CommandLineTool
cwlVersion: v1.0
baseCommand: ["env"]
inputs: []
outputs:
  out:
    type: File
    outputBinding:
      glob: "*.txt"
stdout: out.txt
requirements:
  DockerRequirement:
    dockerPull: alpine
