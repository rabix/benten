class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'
baseCommand:
  - diamond
  - blastx
inputs:
  - id: blockSize
    type: float?
    inputBinding:
      position: 0
      prefix: '--block-size'
    label: sequence block size in billions of letters (default=2.0)
  - id: databaseFile
    type: File
    inputBinding:
      position: 0
      prefix: '--db'
    label: DIAMOND database input file
    doc: Path to the DIAMOND database file.
  - id: outputFormat
    type: Diamond-output_formats.yaml#output_formats?
    inputBinding:
      position: 0
      prefix: '--outfmt'
    label: Format of the output file
    doc: |-
      0   = BLAST pairwise
      5   = BLAST XML
      6   = BLAST tabular
      100 = DIAMOND alignment archive (DAA)
      101 = SAM

      Value 6 may be followed by a space-separated list of these keywords
  - id: queryGeneticCode
    type: int?
    inputBinding:
      position: 0
      prefix: '--min-orf'
    label: Genetic code used for the translation of the query sequences
    doc: >
      Ignore translated sequences that do not contain an open reading frame of
      at least this length.

      By default this feature is disabled for sequences of length below 30, set
      to 20 for sequences of length below 100, and set to 40 otherwise. Setting
      this option to 1 will disable this feature.
  - format: 'edam:format_1929'
    id: queryInputFile
    type: File
    inputBinding:
      position: 0
      prefix: '--query'
    label: Query input file in FASTA
    doc: >
      Path to the query input file in FASTA or FASTQ format (may be gzip
      compressed). If this parameter is omitted, the input will be read from
      stdin
  - id: strand
    type: Diamond-strand_values.yaml#strand?
    inputBinding:
      position: -3
      prefix: '--strand'
    label: Set strand of query to align for translated searches
    doc: >-
      Set strand of query to align for translated searches. By default both
      strands are searched. Valid values are {both, plus, minus}
  - id: taxonList
    type: 'int[]?'
    inputBinding:
      position: 0
      prefix: '--taxonlist'
    label: Protein accession to taxon identifier NCBI mapping file
    doc: >
      Comma-separated list of NCBI taxonomic IDs to filter the database by. Any
      taxonomic rank can be used, and only reference sequences matching one of
      the specified taxon ids will be searched against. Using this option
      requires setting the --taxonmap and --taxonnodes parameters for makedb.
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
  - id: matches
    type: File
    outputBinding:
      glob: $(inputs.queryInputFile.basename).diamond_matches
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
label: Aligns DNA query sequences against a protein reference database
arguments:
  - position: 0
    prefix: '--out'
    valueFrom: $(inputs.queryInputFile.basename).diamond_matches
requirements:
  - class: SchemaDefRequirement
    types:
      - $import: Diamond-strand_values.yaml
      - $import: Diamond-output_formats.yaml
  - class: ResourceRequirement
    ramMin: 1000
  - class: InlineJavascriptRequirement
hints:
  - class: DockerRequirement
    dockerPull: 'buchfink/diamond:version0.9.21'
$schemas:
  - 'http://edamontology.org/EDAM_1.20.owl'
  - 'https://schema.org/version/latest/schema.rdf'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:author: "Arnaud Meng, Maxim Scheremetjew"