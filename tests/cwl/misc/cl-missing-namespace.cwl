# Checks schemadef
class: CommandLineTool
cwlVersion: v1.1
inputs:
  in1: File

baseCommand: echo
outputs:
  out1:
    type: string

stdout: out.txt
requirements:
  InlineJavascriptRequirement: {}
  madeup:y: {}
  evenmoremadeup:z: 22

madeup:x: 22

$namespaces:
  madeup: http://example.com
