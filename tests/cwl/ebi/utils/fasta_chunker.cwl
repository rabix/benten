class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'
baseCommand:
  - python3
inputs:
  - id: chunk_size
    type: int?
    default: 10
  - id: seqs
    type: File
    format: 'edam:format_1929'
outputs:
  - id: chunks
    type: 'File[]'
    outputBinding:
      glob: 'chunks/*_*.fasta'
    format: 'edam:format_1929'
doc: 'based upon code by developers from EMBL-EBI'
label: split FASTA by number of records
arguments:
  - position: 0
    prefix: '-c'
    valueFrom: |
      from Bio import SeqIO
      import os
      currentSequences = []
      os.mkdir("$(runtime.outdir)/chunks")
      for record in SeqIO.parse("$(inputs.seqs.path)", "fasta"):
          currentSequences.append(record)
          if len(currentSequences) == $(inputs.chunk_size):
              fileName = currentSequences[0].id + "_" + currentSequences[-1].id + ".fasta"
              for char in [ "/", " ", ":" ]:
                  fileName = fileName.replace(char, "_")
              SeqIO.write(currentSequences, "$(runtime.outdir)/chunks/"+fileName, "fasta")
              currentSequences = []

      # write any remaining sequences
      if len(currentSequences) > 0:
          fileName = currentSequences[0].id + "_" + currentSequences[-1].id + ".fasta"
          for char in [ "/", " ", ":" ]:
              fileName = fileName.replace(char, "_")
          SeqIO.write(currentSequences, "$(runtime.outdir)/chunks/"+fileName, "fasta")
requirements:
  - class: ResourceRequirement
    ramMin: 100
    coresMax: 1
  - class: InlineJavascriptRequirement
hints:
  - class: DockerRequirement
    dockerPull: biopython/biopython:latest
  - class: SoftwareRequirement
    packages:
      biopython:
        specs:
          - 'https://identifiers.org/rrid/RRID:SCR_007173'
        version:
          - '1.65'
          - '1.66'
          - '1.69'
          - '1.72'
$schemas:
  - 'http://edamontology.org/EDAM_1.16.owl'
  - 'https://schema.org/version/latest/schema.rdf'
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:author: "Michael Crusoe, Maxim Scheremetjew"
