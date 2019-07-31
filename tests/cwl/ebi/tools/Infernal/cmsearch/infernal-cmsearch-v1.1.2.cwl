class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  gx: "http://galaxyproject.org/cwl#"
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'
baseCommand:
  - cmsearch
inputs:
  - id: covariance_model_database
    type: File
    inputBinding:
      position: 1
  - id: cpu
    type: int?
    inputBinding:
      position: 0
      prefix: '--cpu'
    label: Number of parallel CPU workers to use for multithreads
  - default: false
    id: cut_ga
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--cut_ga'
    label: use CM's GA gathering cutoffs as reporting thresholds
  - id: omit_alignment_section
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--noali'
    label: Omit the alignment section from the main output.
    doc: This can greatly reduce the output volume.
  - default: false
    id: only_hmm
    type: boolean?
    inputBinding:
      position: 0
      prefix: '--hmmonly'
    label: 'Only use the filter profile HMM for searches, do not use the CM'
    doc: |
      Only filter stages F1 through F3 will be executed, using strict P-value
      thresholds (0.02 for F1, 0.001 for F2 and 0.00001 for F3). Additionally
      a bias composition filter is used after the F1 stage (with P=0.02
      survival threshold). Any hit that survives all stages and has an HMM
      E-value or bit score above the reporting threshold will be output.
  - format: 'edam:format_1929'
    id: query_sequences
    type: File
    inputBinding:
      position: 2
    streamable: true
  - id: search_space_size
    type: int
    inputBinding:
      position: 0
      prefix: '-Z'
    label: search space size in *Mb* to <x> for E-value calculations
outputs:
  - id: matches
    doc: 'http://eddylab.org/infernal/Userguide.pdf#page=60'
    label: 'target hits table, format 2'
    type: File
    outputBinding:
      glob: $(inputs.query_sequences.basename).cmsearch_matches.tbl
  - id: programOutput
    label: 'direct output to file, not stdout'
    type: File
    outputBinding:
      glob: $(inputs.query_sequences.basename).cmsearch.out
doc: >
  Infernal ("INFERence of RNA ALignment") is for searching DNA sequence
  databases for RNA structure and sequence similarities. It is an implementation
  of a special case of profile stochastic context-free grammars called
  covariance models (CMs). A CM is like a sequence profile, but it scores a
  combination of sequence consensus and RNA secondary structure consensus,
  so in many cases, it is more capable of identifying RNA homologs that
  conserve their secondary structure more than their primary sequence.

  Please visit http://eddylab.org/infernal/ for full documentation.

  Version 1.1.2 can be downloaded from
  http://eddylab.org/infernal/infernal-1.1.2.tar.gz
label: Search sequence(s) against a covariance model database
arguments:
  - position: 0
    prefix: '--tblout'
    valueFrom: $(inputs.query_sequences.basename).cmsearch_matches.tbl
  - position: 0
    prefix: '-o'
    valueFrom: $(inputs.query_sequences.basename).cmsearch.out
hints:
  - class: SoftwareRequirement
    packages:
      infernal:
        specs:
          - 'https://identifiers.org/rrid/RRID:SCR_011809'
        version:
          - 1.1.2
  - class: DockerRequirement
    dockerPull: 'quay.io/biocontainers/infernal:1.1.2--h470a237_1'
  - class: gx:interface
    gx:inputs:
      - gx:name: covariance_model_database
        gx:type: data
        gx:format: 'txt'
      - gx:name: cpu
        gx:type: integer
        gx:optional: True
      - gx:name: cut_ga
        gx:type: boolean
        gx:optional: True
      - gx:name: omit_alignment_section
        gx:type: boolean
        gx:optional: True
      - gx:name: only_hmm
        gx:type: boolean
        gx:optional: True
      - gx:name: query_sequences
        gx:type: data
        gx:format: 'txt'
      - gx:name: search_space_size
        gx:type: integer
        gx:default_value: 1000
        gx:optional: True
requirements:
  - class: InlineJavascriptRequirement
  - class: ResourceRequirement
    ramMin: 2048
    ramMax: 8192
    coresMin: 4
$schemas:
  - 'http://edamontology.org/EDAM_1.16.owl'
  - 'https://schema.org/docs/schema_org_rdfa.html'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"
s:author: "Michael Crusoe, Maxim Scheremetjew"