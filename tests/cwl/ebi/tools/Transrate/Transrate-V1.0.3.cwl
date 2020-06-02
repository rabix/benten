class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'
baseCommand:
  - transrate
inputs:
  - id: in_fasta
    # format: 'edam:format_1929'
    type: File
    inputBinding:
      position: 1
      prefix: '--assembly='
      separate: false
    label: 'Assembly FASTA file'
    doc: >
      Assembly file(s) in FASTA format, comma-separated
  - id: left_fastq
    format: 'edam:format_1930'
    type: File
    inputBinding:
      position: 2
      prefix: '--left='
      separate: false
    label: 'Left reads FASTQ file(s)'
    doc: >
      Left reads file(s) in FASTQ format, comma-separated
  - id: right_fastq
    format: 'edam:format_1930'
    type: File?
    inputBinding:
      position: 3
      prefix: '--right='
      separate: false
    label: 'Right reads FASTQ file(s)'
    doc: >
      Right reads file(s) in FASTQ format, comma-separated
  - id: n_threads
    type: int?
    inputBinding:
      position: 4
      prefix: '--threads='
      separate: false
    label: 'Number of threads allocated'
    doc: >
      Number of threads to use (default: 8)
  - id: log_level
    type: string?
    inputBinding:
      position: 0
      prefix: '--loglevel='
      separate: false
    label: 'LOG file(s)'
    doc: >
      Log level. One of [error, info, warn, debug] (default: info)
outputs:
  - id: transrate_output_dir
    type: Directory
    outputBinding:
      glob: .
# TODO: Find out the name of the evaluation_matrix file
#  - id: evaluation_matrix
#    type: File
#    outputBinding:
#      glob: $(runtime.outdir)/matrix

doc: >
  Analyse a de-novo transcriptome assembly using three kinds of metrics: 1.
  sequence based (if --assembly is given) 2. read mapping based (if --left and
  --right are given) 3. reference based (if --reference is given)

  Documentation at http://hibberdlab.com/transrate
        
label: Transrate - A de-novo transcriptome assembly evaluation facility.

arguments:
  - position: 0
    prefix: '--output='
    separate: false
    valueFrom: $(runtime.outdir)
hints:
  - class: SoftwareRequirement
    packages:
      transrate:
        version:
          - 1.0.3
  - class: DockerRequirement
    dockerPull: 'arnaudmeng/transrate:1.0.3'
$schemas:
  - 'http://edamontology.org/EDAM_1.20.owl'
  - 'https://schema.org/version/latest/schema.rdf'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:author: "Arnaud Meng, Maxim Scheremetjew"