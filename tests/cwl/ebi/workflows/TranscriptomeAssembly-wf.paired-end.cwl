cwlVersion: v1.0
class: Workflow
label: Transcriptome assembly workflow (paired-end version)

requirements:
 - class: MultipleInputFeatureRequirement
 - class: SchemaDefRequirement
   types:
    - $import: ../tools/Trimmomatic/trimmomatic-end_mode.yaml
    - $import: ../tools/Trimmomatic/trimmomatic-phred.yaml
    - $import: ../tools/Trimmomatic/trimmomatic-sliding_window.yaml

inputs:
  read_files:
    type: File[]
    format: edam:format_1930  # Zipped fastq
    label: 'FASTQ read file(s)'
    doc: >
      FASTQ file of reverse reads in Paired End mode
  forward_reads:
    type: File
    format: edam:format_1930  # Zipped fastq
    label: 'Paired-end read file 1'
    doc: >
      Read file 1 in FASTQ format 
  reverse_reads:
    type: File
    format: edam:format_1930  # Zipped fastq
    label: 'Paired-end read file 2'
    doc: >
      Read file 2 in FASTQ format
  end_mode: 
    type: ../tools/Trimmomatic/trimmomatic-end_mode.yaml#end_mode
    label: 'read -end mode format'
    doc: >
      Read -end mode format to be specify to Trimmomatic
  trimmomatic_phred:
    type: ../tools/Trimmomatic/trimmomatic-phred.yaml#phred
    label: 'quality score format'
    default: '33'
    doc: >
      Either PHRED "33" or "64" specifies the base quality encoding. Default: 64
  trimmomatic_slidingWindow:
    type: ../tools/Trimmomatic/trimmomatic-sliding_window.yaml#slidingWindow
    label: 'read filtering sliding window'
    default:
      windowSize: 4
      requiredQuality: 15
    doc: >
      Perform a sliding window trimming, cutting once the average quality
      within the window falls below a threshold. By considering multiple
      bases, a single poor quality base will not cause the removal of high
      quality data later in the read.
      <windowSize> specifies the number of bases to average across
      <requiredQuality> specifies the average quality required
  trinity_max_mem:
    type: string
    label: 'maximum memory allocated to Trinity'
    doc: >
      Suggested max memory to use by Trinity where limiting can be enabled.
      (jellyfish, sorting, etc) provided in Gb of RAM, ie. --max_memory 10G
  trinity_cpu:
    type: int?
    label: 'number of CPUs allocated'
    doc: > 
      number of CPUs to use, default: 2
  trinity_seq_type:
    type: string
    label: 'read file(s) format'
    doc: >
      type of reads: (fa or fq)
  trinity_ss_lib_type:
    type: string
    label: 'Strand-specific RNA-Seq read orientation'
    doc: >
      Strand-specific RNA-Seq read orientation. if paired: RF or FR, if single:
      F or R. (dUTP method = RF). See web documentation

outputs:
  raw_qc_report:
    type: File[]
#    format: TODO: Zip format not found in edam ontology
    outputSource: generate_raw_stats/zipped_report
  raw_html_report:
    type: File[]
    format: edam:format_2331
    outputSource: generate_raw_stats/html_report
  filtered_qc_report:
    type: File[]
    outputSource: generate_filtered_stats/zipped_report
  filtered_html_report:
    type: File[]
    format: edam:format_2331
    outputSource: generate_filtered_stats/html_report
  trimmomatic_log_file:
      type: File?
      outputSource: filter_reads/log_file
  forward_reads_paired:
    type: File
    format: edam:format_1930
    outputSource: filter_reads/reads1_trimmed
  forward_reads_unpaired:
    type: File?
    format: edam:format_1930
    outputSource: filter_reads/reads1_trimmed_unpaired
  reverse_reads_paired:
    type: File
    format: edam:format_1930
    outputSource: filter_reads/reads2_trimmed_paired
  reverse_reads_unpaired:
    type: File?
    format: edam:format_1930
    outputSource: filter_reads/reads2_trimmed_unpaired
  assembly_output_dir:
    type: Directory
    outputSource: run_assembly/assembly_dir
  assembled_contigs:
    type: File
    format: edam:format_1929 # FASTA
    outputSource: run_assembly/assembled_contigs
#    TODO: Get this back in
#  evaluation_matrix:
#    type: File
#    format: edam:format_3752 # CSV
#    outputSource: evaluate_contigs/evaluation_matrix
  transrate_output_dir:
    type: Directory
    outputSource: evaluate_contigs/transrate_output_dir

steps:
  generate_raw_stats:
    label: Generates a QC for the provided read file(s).
    doc: |
      Provide reverse and forward read files for paired-end (PE)
      or a single read file for single-end (SE).
    run: ../tools/FastQC/FastQC-v0.11.7.cwl
    in:
      in_fastq: read_files
    out: [ zipped_report, html_report ]

  filter_reads:
    label: Filtering and trimmming read file(s)
    doc: |
      Low quality trimming (low quality ends and sequences with < quality scores
      less than 15 over a 4 nucleotide wide window are removed)
    run: ../tools/Trimmomatic/Trimmomatic-v0.36.cwl
    in:
      reads1: forward_reads
      reads2: reverse_reads
      phred: trimmomatic_phred
      leading: { default: 3 }
      trailing: { default: 3 }
      end_mode: end_mode
      minlen: { default: 100 }
      slidingwindow: trimmomatic_slidingWindow
    out: [log_file, reads1_trimmed, reads1_trimmed_unpaired, reads2_trimmed_paired, reads2_trimmed_unpaired]

  run_assembly:
    label: Runs the actual assembly
    doc: |
      provide filtered/trimmed read file(s)
    run: ../tools/Trinity/Trinity-V2.6.5.paired-end.cwl
    in:
      left_reads: filter_reads/reads1_trimmed
      right_reads: filter_reads/reads2_trimmed_paired
      trinity_max_mem: trinity_max_mem
      trinity_cpu: trinity_cpu
      trinity_seq_type: trinity_seq_type
      trinity_ss_lib_type: trinity_ss_lib_type
    out: [ assembly_dir, assembled_contigs ]

  generate_filtered_stats:
    label: Generates a QC for the filtered read file(s).
    doc: |
      Provide filtered/trimmed read file(s)
    run: ../tools/FastQC/FastQC-v0.11.7.cwl
    in:
      in_fastq:
        source: [filter_reads/reads1_trimmed]
        linkMerge: merge_flattened
    out: [ zipped_report, html_report ]

  evaluate_contigs:
    label: Evaluates the contig quality.
    doc: |
      Provide the assembled contigs (FASTA file)
    run: ../tools/Transrate/Transrate-V1.0.3.cwl
    in:
      in_fasta: run_assembly/assembled_contigs
      left_fastq: filter_reads/reads1_trimmed
      right_fastq: filter_reads/reads2_trimmed_paired
    out: [ transrate_output_dir ]

$namespaces:
 edam: http://edamontology.org/
 s: http://schema.org/
$schemas:
 - http://edamontology.org/EDAM_1.16.owl
 - https://schema.org/docs/schema_org_rdfa.html
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2019"
s:author: "Arnaud Meng, Maxim Scheremetjew"