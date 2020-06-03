class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  s: 'http://schema.org/'
baseCommand:
  - cat
inputs:
  - id: files
    type: 'File[]'
    inputBinding:
      position: 1
    streamable: true
  - id: outputFileName
    type: string
outputs:
  - id: result
    type: File
    outputBinding:
      glob: $(inputs.outputFileName)
      outputEval: |
        ${ self[0].format = inputs.files[0].format;
           return self; }

doc: >
  The cat (short for “concatenate“) command is one of the most frequently used command in
  Linux/Unix like operating systems. cat command allows us to create single or multiple
  files, view contain of file, concatenate files and redirect output in terminal or files.
label: Redirecting Multiple Files Contain in a Single File
requirements:
  - class: ResourceRequirement
    ramMin: 100
    coresMax: 1
  - class: InlineJavascriptRequirement
hints:
  - class: DockerRequirement
    dockerPull: 'alpine:3.7'
stdout: $(inputs.outputFileName)
$schemas:
  - 'https://schema.org/version/latest/schema.rdf'
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:author: "Michael Crusoe, Maxim Scheremetjew"