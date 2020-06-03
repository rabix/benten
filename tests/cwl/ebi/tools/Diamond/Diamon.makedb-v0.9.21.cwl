class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  gx: "http://galaxyproject.org/cwl#"
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'
baseCommand:
  - diamond
  - makedb
inputs:
  - format: 'edam:format_1929'
    id: inputRefDBFile
    type: File
    inputBinding:
      position: 0
      prefix: '--in'
    label: Input protein reference database file
    doc: >
      Path to the input protein reference database file in FASTA format (may be
      gzip compressed).
      If this parameter is omitted, the input will be read from stdin.
  - id: taxonMapFile
    type: File?
    inputBinding:
      position: 0
      prefix: '--taxonmap'
    label: Protein accession to taxon identifier NCBI mapping file
    doc: >
      Path to mapping file that maps NCBI protein accession numbers to taxon ids
      (gzip compressed).

      This parameter is optional and needs to be supplied in order to provide
      taxonomy features.

      The file can be downloaded from NCBI:
      ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/prot.accession2taxid.gz.
  - id: taxonNodesFiles
    type: File?
    inputBinding:
      position: 0
      prefix: '--taxonnodes'
    label: Nodes.dmp file from the NCBI taxonomy
    doc: >
      Path to the nodes.dmp file from the NCBI taxonomy. This parameter is
      optional and needs to be supplied in order to provide taxonomy features. The file is contained within this
      archive downloadable at NCBI:

      ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdmp.zip
  - id: threads
    type: int?
    inputBinding:
      position: 0
      prefix: '--threads'
    label: Number of CPU threads
    doc: >
      Number of CPU threads. By default, the program will auto-detect and use
      all available virtual cores on the machine.
outputs:
  - id: diamondDatabaseFile
    type: File
    outputBinding:
      glob: $(inputs.inputRefDBFile.nameroot).dmnd
    format: 'edam:format_2333'
doc: |
  DIAMOND is a sequence aligner for protein and translated DNA searches,
  designed for high performance analysis of big sequence data.

  The key features are:
        + Pairwise alignment of proteins and translated DNA at 500x-20,000x speed of BLAST.
        + Frameshift alignments for long read analysis.
        + Low resource requirements and suitable for running on standard desktops or laptops.
        + Various output formats, including BLAST pairwise, tabular and XML, as well as taxonomic classification.

  Please visit https://github.com/bbuchfink/diamond for full documentation.

  Releases can be downloaded from https://github.com/bbuchfink/diamond/releases
label: >-
  diamond makedb: Sets up a reference protein database (in binary file format)
  for DIAMOND
arguments:
  - position: 0
    prefix: '--db'
    valueFrom: $(inputs.inputRefDBFile.nameroot).dmnd
requirements:
  - class: ResourceRequirement
    ramMin: 1024
  - class: InlineJavascriptRequirement
hints:
  - class: DockerRequirement
    dockerPull: 'buchfink/diamond:version0.9.21'
  - class: gx:interface
    gx:inputs:
      - gx:name: inputRefDBFile
        gx:type: data
        gx:format: 'txt'
      - gx:name: taxonMapFile
        gx:type: data
        gx:format: 'txt'
        gx:optional: True
      - gx:name: taxonNodesFiles
        gx:type: data
        gx:format: 'txt'
        gx:optional: True
      - gx:name: threads
        gx:type: integer
        gx:optional: True
$schemas:
  - 'http://edamontology.org/EDAM_1.20.owl'
  - 'https://schema.org/version/latest/schema.rdf'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:author: "Arnaud Meng, Maxim Scheremetjew"
