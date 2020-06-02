class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  gx: "http://galaxyproject.org/cwl#"
  edam: 'http://edamontology.org/'
  iana: 'https://www.iana.org/assignments/media-types/'
  s: 'http://schema.org/'
baseCommand:
  - run_BUSCO.py
inputs:
  - id: blastSingleCore
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--blast_single_core'
    label: Force tblastn to run on a single core
    doc: |
      Force tblastn to run on a single core and ignore the --cpu argument for
      this step only. Useful if inconsistencies when using multiple threads are
      noticed
  - id: cpu
    type: int?
    inputBinding:
      position: 0
      prefix: '--cpu'
    label: 'Specify the number of threads/cores to use (default: 1)'
  - id: evalue
    type: float?
    inputBinding:
      position: 0
      prefix: '--evalue'
    label: E-value cutoff for BLAST searches
    doc: |
      Allowed formats: 0.001 or 1e-03 (default: 1e-03).
  - id: force
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--force'
    label: Force rewriting of existing files/folders
    doc: |
      Must be used when output files with the provided name already exist.
  - id: help
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--help'
    label: Show this help message and exit
  - id: lineage
    type: Directory
    inputBinding:
      position: 0
      prefix: '--lineage_path'
    label: Location of the BUSCO lineage data to use (e.g. fungi_odb9)
    doc: |
      Specify location of the BUSCO lineage data to be used.
      Visit http://busco.ezlab.org/ for available lineages.
  - id: long
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--long'
    label: 'Turn on Augustus optimization mode for self-training (default: Off)'
    doc: |
      Adds substantially to the run time!
      Can improve results for some non-model organisms.
  - id: mode
    type: BUSCO-assessment_modes.yaml#assessment_modes
    inputBinding:
      position: 0
      prefix: '--mode'
    label: 'Sets the assessment MODE: genome, proteins, transcriptome'
    doc: |
      Specify which BUSCO analysis mode to run.
      There are three valid modes:
      - geno or genome, for genome assemblies (DNA).
      - tran or transcriptome, for transcriptome assemblies (DNA).
      - prot or proteins, for annotated gene sets (protein).
  - id: outputName
    type: string
    inputBinding:
      position: 0
      prefix: '--out'
    label: Name to use for the run and all temporary files (appended)
    doc: |
      Give your analysis run a recognisable short name.
      Output folders and files will be labelled (prepended) with this name.
      WARNING: do not provide a path.
  - id: quiet
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--quiet'
    label: 'Disable the info logs, display only errors'
  - id: regionLimit
    type: int?
    inputBinding:
      position: 0
      prefix: '--limit'
    label: 'How many candidate regions to consider (integer, default: 3)'
    doc: >
      NB: this limit is on scaffolds, chromosomes, or transcripts, not
      individual hit regions.
  - id: restart
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--restart'
    label: Restart the BUSCO run from the last successfully-completed step
    doc: >
      NB: If all the required results files from previous steps are not all
      found then this will not be possible.
  - format: 'edam:format_1929'
    id: sequenceFile
    type: File
    inputBinding:
      position: 0
      prefix: '--in'
    label: Sequence file in FASTA format
    doc: |
      Input sequence file in FASTA format (not compressed/zipped!).
      Can be an assembled genome (genome mode) or transcriptome (DNA,
      transcriptome mode), or protein sequences from an annotated gene set
      (proteins mode).
      NB: select just one transcript/protein per gene for your input,
      otherwise they will appear as 'Duplicated' matches.
  - id: species
    type: string?
    inputBinding:
      position: 0
      prefix: '--species'
    label: Name of existing Augustus species gene finding parameters
    doc: |
      See Augustus documentation for available options.
      Each lineage has a default species (see below on assessment sets).
      Selecting a closely-related species usually produces better results.
  - id: tarzip
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--tarzip'
    label: Results folders with many files will be tarzipped
  - id: tempPath
    type: Directory?
    inputBinding:
      position: 0
      prefix: '--tmp'
    label: 'Where to store temporary files (default: ./tmp)'
  - id: version
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--version'
    label: Show this version information and exit
outputs:
  - id: blastOutput
    doc: |
      tBLASTn results, not created for assessment of proteins.
      File: tblastn_XXXX.txt = tabular tBLASTn results
      File: coordinates_XXXX.txt = locations of BUSCO matches (genome mode)
    type: Directory
    outputBinding:
      glob: run_$(inputs.outputName)/blast_output
  - id: fullTable
    doc: >
      Contains the complete results in a tabular format with scores and lengths
      of BUSCO matches, and coordinates (for genome mode) or gene/protein IDs
      (for transcriptome or proteins mode).
    type: File
    outputBinding:
      glob: run_$(inputs.outputName)/full_table_*.tsv
    format: 'iana:text/tab-separated-values'
  - id: hmmerOutput
    label: Tabular format HMMER output of searches with BUSCO HMMs
    type: Directory
    outputBinding:
      glob: run_$(inputs.outputName)/hmmer_output
  - id: missingBUSCOs
    label: Contains a list of missing BUSCOs
    type: File
    outputBinding:
      glob: run_$(inputs.outputName)/missing_busco_list_*.tsv
    format: 'iana:text/tab-separated-values'
  - id: shortSummary
    doc: |
      Contains a plain text summary of the results in BUSCO notation.
      Also gives a brief breakdown of the metrics.
    type: File
    outputBinding:
      glob: run_$(inputs.outputName)/short_summary_*.txt
  - id: translatedProteins
    label: >-
      Transcript sequence translations, only created during transcriptome
      assessment
    type: Directory
    outputBinding:
      glob: run_$(inputs.outputName)/translated_proteins
doc: >
  BUSCO v3 provides quantitative measures for the assessment of genome assembly,
  gene set, and transcriptome completeness, based on evolutionarily-informed expectations
  of gene content from near-universal single-copy orthologs selected from OrthoDB v9.
  BUSCO assessments are implemented in open-source software, with a large
  selection of lineage-specific sets of Benchmarking Universal Single-Copy Orthologs. These
  conserved orthologs are ideal candidates for large-scale phylogenomics studies, and the
  annotated BUSCO gene models built during genome assessments provide a comprehensive gene
  predictor training set for use as part of genome annotation pipelines.

  Please visit http://busco.ezlab.org/ for full documentation.

  The BUSCO assessment software distribution is available from the public GitLab
  project:
  https://gitlab.com/ezlab/busco where it can be downloaded or cloned using a
  git client (git clone https://gitlab.com/ezlab/busco.git). We encourage users to opt for
  the git client option in order to facilitate future updates.

  BUSCO is written for Python 3.x and Python 2.7+. It runs with the standard
  packages. We recommend using Python3 when available.
label: >-
  Assesses genome assembly and annotation completeness with single-copy
  orthologs
requirements:
  - class: ResourceRequirement
    coresMin: 1
  - class: InlineJavascriptRequirement
  - class: SchemaDefRequirement
    types:
      - $import: BUSCO-assessment_modes.yaml
hints:
  - class: SoftwareRequirement
    packages:
      BUSCO:
        specs:
          - 'https://identifiers.org/rrid/RRID:SCR_015008'
        version:
          - 3.0.2
  - class: DockerRequirement
    dockerPull: 'comics/busco:3.0.2'
  - class: gx:interface
    gx:inputs:
      - gx:name: blastSingleCore
        gx:type: boolean
        gx:optional: True
      - gx:name: cpu
        gx:type: integer
        gx:optional: True
      - gx:name: evalue
        gx:type: float
        gx:optional: True
      - gx:name: force
        gx:type: boolean
        gx:optional: True
      - gx:name: help
        gx:type: boolean
        gx:optional: True
      - gx:name: lineage
        gx:type: data
      - gx:name: long
        gx:type: boolean
        gx:optional: True
      - gx:name: mode
        gx:value: tran
        gx:type: text
      - gx:name: outputName
        gx:value: TEST
        gx:type: text
      - gx:name: quiet
        gx:type: boolean
        gx:optional: True
      - gx:name: regionLimit
        gx:type: integer
        gx:optional: True
      - gx:name: restart
        gx:type: boolean
        gx:optional: True
      - gx:name: sequenceFile
        gx:format: 'txt'
        gx:type: data
      - gx:name: species
        gx:type: text
        gx:optional: True
      - gx:name: tarzip
        gx:type: boolean
        gx:optional: True
      - gx:name: tempPath
        gx:type: data
        gx:optional: True
      - gx:name: version
        gx:type: boolean
        gx:optional: True
$schemas:
  - 'http://edamontology.org/EDAM_1.20.owl'
  - 'https://schema.org/version/latest/schema.rdf'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:author: "Arnaud Meng, Maxim Scheremetjew"
