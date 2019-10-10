# Checks input generation for secondary files on input and output
# Checks mixtures of JS and parameter references
# Checks JS expressions for secondary files

class: CommandLineTool
cwlVersion: v1.1
inputs:
  in1:
    type: File
    inputBinding: 
      position: 1
      valueFrom: A_$(inputs.in1)_B_${return inputs.in1.secondaryFiles}_C_$(inputs.in1)
  in5:
    type: File
    secondaryFiles:
      - .s1
      - .s2
    inputBinding: 
      position: 1
      valueFrom: A_$(inputs.in1)_B_${return inputs.in2.secondaryFiles}_C_$(inputs.in1)


baseCommand: echo
arguments:
  - valueFrom: $(runtime)
outputs:
  out1:
    type: string
    outputBinding:
      glob: out.txt
      loadContents: true
      outputEval: $(self)_D_$(runtime)

stdout: out.txt
requirements:
  InlineJavascriptRequirement: {}