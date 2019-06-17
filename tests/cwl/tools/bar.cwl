# A simple tool that just prints "bar <int>"

# cwltoil tools/bar.cwl

class: CommandLineTool
cwlVersion: v1.0
inputs:
  in1: int
baseCommand: [echo]
outputs:
  out1:
    type: string
    outputBinding:
      outputEval: ${return "bar " + inputs.in1}

requirements:
  InlineJavascriptRequirement: {}
