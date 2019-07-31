cwlVersion: v1.0
class: Workflow
label: Chunked version of phmmer-v3.2.cwl

requirements:
 ScatterFeatureRequirement: {}

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
    inputBinding:
      position: 1
    label: Query sequence(s) file
    doc: >
      Search one or more query protein sequences against a protein sequence
      database.
  - id: seqdb
    type: File
    inputBinding:
      position: 2
    label: Target database of sequences
  - id: fullPhmmerMatches
    type: string
    default: full_phmmer_matches
  - id: fullPhmmerOutput
    type: string
    default: full_phmmer_output
outputs:
  - id: matches
    type: File
    outputSource: combine_phmmer_matches/result
#    format: edam:format_1929  # Tabular format
  - id: programOutput
    type: File
    outputSource: combine_phmmer_output/result

steps:
  split_seqs:
    run: ../utils/fasta_chunker.cwl
    in:
      seqs: seqFile
      chunk_size: { default: 500 }
    out: [ chunks ]

  calculate_phmmer_matches:
    label: Calculates phmmer matches on chunked sequence files
    run: ../tools/HMMER/phmmer-v3.2.cwl
    in:
      seqFile: split_seqs/chunks
      seqdb: seqdb
    scatter: seqFile
    out: [ matches, programOutput ]

  combine_phmmer_matches:
    run: ../utils/concatenate.cwl
    in:
      files: calculate_phmmer_matches/matches
      outputFileName: fullPhmmerMatches
    out: [ result ]

  combine_phmmer_output:
    run: ../utils/concatenate.cwl
    in:
      files: calculate_phmmer_matches/programOutput
      outputFileName: fullPhmmerOutput
    out: [ result ]

$namespaces:
 edam: http://edamontology.org/
 s: http://schema.org/
$schemas:
 - http://edamontology.org/EDAM_1.16.owl
 - https://schema.org/docs/schema_org_rdfa.html

s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:author: "Maxim Scheremetjew"