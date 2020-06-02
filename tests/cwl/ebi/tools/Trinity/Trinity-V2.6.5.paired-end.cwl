class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'

requirements:
  SchemaDefRequirement:
    types:
      - $import: trinity-ss_lib_type.yaml
      - $import: trinity-seq_type.yaml

baseCommand: [ /usr/local/bin/trinityrnaseq/Trinity, --full_cleanup ]

inputs:
  - id: trinity_seq_type
    type: string
    default: fa
    inputBinding:
      position: 1
      prefix: '--seqType'
    label: 'read file(s) format'
    doc: >
      type of reads: (fa or fq)
  - id: trinity_max_mem
    type: string
    default: 20G
    inputBinding:
      position: 2
      prefix: '--max_memory'
    label: 'maximum memory allocated'
    doc: >
      Suggested max memory to use by Trinity where limiting can be enabled.
      (jellyfish, sorting, etc) provided in Gb of RAM, ie. --max_memory 10G
  - id: left_reads
    type: File
    inputBinding:
      position: 3
      prefix: '--left'
      itemSeparator: ","
    label: 'left read(s)'
    doc: >
      left reads, one or more file names (separated by commas, no spaces)
  - id: right_reads
    type: File
    inputBinding:
      position: 4
      prefix: '--right'
      itemSeparator: ","
    label: 'right read(s)'
    doc: >
      right reads, one or more file names (separated by commas, no spaces)
  - id: trinity_ss_lib_type
    type: string
    inputBinding:
      position: 6
      prefix: '--SS_lib_type'
    label: 'Strand-specific RNA-Seq read orientation'
    doc: >
      Strand-specific RNA-Seq read orientation. if paired: RF or FR, if single:
      F or R. (dUTP method = RF). See web documentation
  - id: trinity_cpu
    type: int?
    default: 2
    inputBinding:
      position: 7
      prefix: '--CPU'
    label: 'number of CPUs allocated'
    doc: >
      number of CPUs to use by Trinity
  - id: no_normalize_reads
    type: boolean?
    inputBinding:
      position: 8
      prefix: '--no_normalize_reads'
    label: 'Do *not* run in silico normalization of reads. default: normalize reads'
  - id: normalize_by_read_set
    type: boolean?
    inputBinding:
      position: 9
      prefix: '--normalize_by_read_set'
    label: 'Run normalization separate for each pair of fastq files'

outputs:
  - id: assembly_dir
    label: Assembly directory containing assembly results
    type: Directory
    outputBinding:
      glob: "."
  - id: assembled_contigs
    label: Generated contigs
    type: File
    outputBinding:
      glob: "*fasta"

doc: >
  Trinity, developed at the Broad Institute and the Hebrew University of
  Jerusalem,  represents a novel method for the efficient and robust de novo
  reconstruction  of transcriptomes from RNA-seq data.  Trinity combines three
  independent software modules: Inchworm, Chrysalis, and  Butterfly, applied
  sequentially to process large volumes of RNA-seq reads.

  Documentation at https://github.com/trinityrnaseq/trinityrnaseq/wiki

label: Trinity assembles transcript sequences from Illumina RNA-Seq data.

arguments:
  - prefix: '--output'
    valueFrom: $(runtime.outdir)/trinity_out_dir/

hints:
  - class: SoftwareRequirement
    packages:
      Trinity:
        version:
          - 2.6.5
  - class: DockerRequirement
    dockerPull: 'trinityrnaseq/trinityrnaseq:2.6.5'

$schemas:
  - 'http://edamontology.org/EDAM_1.16.owl'
  - 'https://schema.org/version/latest/schema.rdf'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:author: "Arnaud Meng, Maxim Scheremetjew"
