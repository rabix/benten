cwlVersion: v1.0
class: CommandLineTool
inputs:
  exclusive_parameters:
    type:
      - type: record
        name: input_file_1
        fields:
          input_file_1:
            type: File
            inputBinding:
              prefix: -file-one
            label: this is a file of type 1
      - type: record
        name: input_file_2
        fields:
          input_file_2:
            type: File
            inputBinding:
              prefix: -file-two
            label: this is a file of type 2
  another_parameter:
    type: string
    id: input_another_parameter
    inputBinding:
      position: 1
      prefix: -another_parameter
    label: This is a regular string parameter.
outputs: []
baseCommand: echo