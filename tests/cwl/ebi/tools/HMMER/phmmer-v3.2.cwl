class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  gx: "http://galaxyproject.org/cwl#"
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'
baseCommand:
  - phmmer
inputs:
  - id: bitscoreThreshold
    type: int?
    inputBinding:
      position: 0
      prefix: '-T'
    label: report sequences >= this bit score threshold in output
  - id: cpu
    type: int?
    inputBinding:
      position: 0
      prefix: '--cpu'
    label: Number of parallel CPU workers to use for multithreads
  - id: seqFile
    type: File
    format: 'edam:format_1929'
    inputBinding:
      position: 1
    label: Query sequence(s) file
    doc: >
      Search one or more query protein sequences against a protein sequence
      database.
  - id: seqdb
    type: File
    format: 'edam:format_1929'
    inputBinding:
      position: 2
    label: Target database of sequences
outputs:
  - id: matches
    type: File
    outputBinding:
      glob: $(inputs.seqFile.basename).phmmer_matches.tblout
  - id: programOutput
    type: File
    outputBinding:
      glob: $(inputs.seqFile.basename).phmmer_matches.out
doc: >
  The phmmer and jackhmmer programs search a single protein sequence against a
  protein sequence database, akin to BLASTP and PSIBLAST, respectively. (Internally, they just
  produce a profile HMM from the query sequence, then run HMM searches.)
  Please visit https://github.com/EddyRivasLab/hmmer for full documentation.

  Releases can be downloaded from https://github.com/EddyRivasLab/hmmer/releases
label: >-
  Search a single protein sequence against a protein sequence database.
  (BLASTP-like)
arguments:
  - position: 0
    prefix: '--tblout'
    valueFrom: $(inputs.seqFile.basename).phmmer_matches.tblout
  - position: 0
    prefix: '-o'
    valueFrom: $(inputs.seqFile.basename).phmmer_matches.out
requirements:
  - class: ResourceRequirement
    ramMin: 1024
    coresMin: 2
    coresMax: 4
  - class: InlineJavascriptRequirement
hints:
  - class: DockerRequirement
    dockerPull: quay.io/biocontainers/hmmer:3.2--hfc679d8_3
  - class: gx:interface
    gx:inputs:
      - gx:name: bitscoreThreshold
        gx:type: integer
        gx:optional: True
      - gx:name: cpu
        gx:type: integer
        gx:optional: True
      - gx:name: seqFile
        gx:type: data
        gx:format: 'txt'
      - gx:name: seqdb
        gx:type: data
        gx:format: 'txt'
$schemas:
  - 'http://edamontology.org/EDAM_1.20.owl'
  - 'https://schema.org/version/latest/schema.rdf'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:author: "Arnaud Meng, Maxim Scheremetjew"
