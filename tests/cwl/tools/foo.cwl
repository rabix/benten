# A simple tool that just prints "foo <int>"

# cwltoil tools/foo.cwl

class: CommandLineTool
cwlVersion: v1.0
inputs:
  in1: int
baseCommand: [echo]
outputs:
  out1:
    type: string
    outputBinding:
      outputEval: ${return "foo " + inputs.in1}

requirements:
  InlineJavascriptRequirement: {}
