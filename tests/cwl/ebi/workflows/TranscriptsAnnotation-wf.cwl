cwlVersion: v1.0
class: Workflow
label: Transcripts annotation workflow

requirements:
 - class: SubworkflowFeatureRequirement
 - class: SchemaDefRequirement
   types:
    - $import: ../utils/esl-reformat-replace.yaml
    - $import: ../tools/BUSCO/BUSCO-assessment_modes.yaml
    - $import: ../tools/InterProScan/InterProScan-apps.yaml
    - $import: ../tools/InterProScan/InterProScan-protein_formats.yaml

inputs:
  transcriptsFile:
    type: File
    format: edam:format_1929  # FASTA
  singleBestOnly: boolean?
  replace: ../utils/esl-reformat-replace.yaml#replace?
  phmmerSeqdb:
    type: File
    format: edam:format_1929  # FASTA
  diamondSeqdb: File
  i5Databases: Directory
  i5Applications: ../tools/InterProScan/InterProScan-apps.yaml#apps[]?
  i5OutputFormat: ../tools/InterProScan/InterProScan-protein_formats.yaml#protein_formats[]?
  blockSize: float?
  covariance_models: File[]
  clanInfoFile: File
  cmsearchCores: int
  buscoMode: ../tools/BUSCO/BUSCO-assessment_modes.yaml#assessment_modes
  buscoOutputName: string
  buscoLineage: Directory

outputs:
  peptide_sequences:
    type: File
    outputSource: identify_coding_regions/peptide_sequences
  coding_regions:
    type: File
    outputSource: identify_coding_regions/coding_regions
  gff3_output:
    type: File
    outputSource: identify_coding_regions/gff3_output
  bed_output:
    type: File
    outputSource: identify_coding_regions/bed_output
  reformatted_sequences:
    type: File
    outputSource: remove_asterisks_and_reformat/reformatted_sequences
  i5Annotations:
    type: File
    outputSource: functional_analysis/i5Annotations
  phmmer_matches:
    type: File
    outputSource: calculate_phmmer_matches/matches
  diamond_matches:
    type: File
    outputSource: calculate_diamond_matches/matches
  deoverlapped_matches:
    type: File
    outputSource: identify_nc_rna/deoverlapped_matches
  busco_short_summary:
    type: File
    outputSource: run_transcriptome_assessment/shortSummary
  busco_full_table:
    type: File
    outputSource: run_transcriptome_assessment/fullTable
  busco_missing_buscos:
    type: File
    outputSource: run_transcriptome_assessment/missingBUSCOs
  busco_hmmer_output:
    type: Directory
    outputSource: run_transcriptome_assessment/hmmerOutput
  busco_translated_proteins:
    type: Directory
    outputSource: run_transcriptome_assessment/translatedProteins
  busco_blast_output:
    type: Directory
    outputSource: run_transcriptome_assessment/blastOutput

steps:
  identify_coding_regions:
    label: Identifies candidate coding regions within transcript sequences
    run: TransDecoder-v5-wf-2steps.cwl
    in:
      transcriptsFile: transcriptsFile
      singleBestOnly: singleBestOnly
    out: [ peptide_sequences, coding_regions, gff3_output, bed_output ]

  remove_asterisks_and_reformat:
    label: Removes asterisks characters from given peptide sequences
    run: ../utils/esl-reformat.cwl
    in:
      sequences: identify_coding_regions/peptide_sequences
      replace: replace
    out: [ reformatted_sequences ]

  functional_analysis:
    doc: |
        Matches are generated against predicted CDS, using a sub set of databases
        from InterPro.
    run: InterProScan-v5-chunked-wf.cwl
    in:
      inputFile: remove_asterisks_and_reformat/reformatted_sequences
      databases: i5Databases
      applications: i5Applications
      outputFormat: i5OutputFormat
    out: [ i5Annotations ]

  calculate_phmmer_matches:
    label: Calculates phmmer matches
    run: ../tools/HMMER/phmmer-v3.2.cwl
    in:
      seqFile: identify_coding_regions/peptide_sequences
      seqdb: phmmerSeqdb
    out: [ matches, programOutput ]

  calculate_diamond_matches:
    label: Calculates Diamond matches
    run: ../tools/Diamond/Diamon.blastx-v0.9.21.cwl
    in:
      queryInputFile: transcriptsFile
      databaseFile: diamondSeqdb
      blockSize: blockSize
    out: [ matches ]

  identify_nc_rna:
    label: Identifies non-coding RNAs using Rfams covariance models
    run: cmsearch-multimodel-wf.cwl
    in:
      query_sequences: transcriptsFile
      covariance_models: covariance_models
      clan_info: clanInfoFile
      cores: cmsearchCores
    out: [ deoverlapped_matches ]

  run_transcriptome_assessment:
    label: Performs transcriptome assessment using BUSCO
    run: ../tools/BUSCO/BUSCO-v3.cwl
    in:
      mode: buscoMode
      sequenceFile: transcriptsFile
      outputName: buscoOutputName
      lineage: buscoLineage
    out: [ shortSummary, fullTable, missingBUSCOs, hmmerOutput, translatedProteins, blastOutput ]


$namespaces:
 edam: http://edamontology.org/
 s: http://schema.org/
$schemas:
 - http://edamontology.org/EDAM_1.16.owl
 - https://schema.org/docs/schema_org_rdfa.html

s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"