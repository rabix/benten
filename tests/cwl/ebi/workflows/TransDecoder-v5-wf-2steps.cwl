class: Workflow
cwlVersion: v1.0
label: >-
  TransDecoder 2 step workflow, running TransDecoder.LongOrfs (step 1) followed
  by TransDecoder.Predict (step2)
$namespaces:
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'
inputs:
  singleBestOnly:
    type: boolean?
  transcriptsFile:
    format: edam:format_1929  # FASTA
    type: File
outputs:
  bed_output:
    outputSource: predict_coding_regions/bed_output
    type: File
  coding_regions:
    outputSource: predict_coding_regions/coding_regions
    type: File
  gff3_output:
    outputSource: predict_coding_regions/gff3_output
    type: File
  peptide_sequences:
    outputSource: predict_coding_regions/peptide_sequences
    type: File
steps:
  extract_long_orfs:
    label: Extracts the long open reading frames
    run: ../tools/TransDecoder/TransDecoder.LongOrfs-v5.cwl
    in:
      transcriptsFile: transcriptsFile
    out:
      - workingDir
  predict_coding_regions:
    label: Predicts the likely coding regions
    run: ../tools/TransDecoder/TransDecoder.Predict-v5.cwl
    in:
      longOpenReadingFrames: extract_long_orfs/workingDir
      singleBestOnly: singleBestOnly
      transcriptsFile: transcriptsFile
    out:
      - bed_output
      - coding_regions
      - gff3_output
      - peptide_sequences
$schemas:
  - 'http://edamontology.org/EDAM_1.16.owl'
  - 'https://schema.org/version/latest/schema.rdf'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:author: "Maxim Scheremetjew"