class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  gx: "http://galaxyproject.org/cwl#"
  edam: 'http://edamontology.org/'
  s: 'http://schema.org/'
baseCommand:
  - cmsearch-deoverlap.pl
inputs:
  - id: clan_information
    type: File?
    inputBinding:
      position: 0
      prefix: '--clanin'
    label: clan information on the models provided
    doc: Not all models provided need to be a member of a clan
  - id: cmsearch_matches
    type: File
    inputBinding:
      position: 1
      valueFrom: $(self.basename)
outputs:
  - id: deoverlapped_matches
    doc: 'http://eddylab.org/infernal/Userguide.pdf#page=60'
    label: 'target hits table, format 2'
    type: File
    outputBinding:
      glob: '*.deoverlapped'
doc: >-
  https://github.com/nawrockie/cmsearch_tblout_deoverlap/blob/master/00README.txt
label: Remove lower scoring overlaps from cmsearch --tblout files.
requirements:
  - class: EnvVarRequirement
    envDef:
      LC_ALL: C
  - class: ResourceRequirement
    ramMin: 100
    coresMax: 1
  - class: InitialWorkDirRequirement
    listing:
      - $(inputs.cmsearch_matches)
  - class: InlineJavascriptRequirement
hints:
  - class: SoftwareRequirement
    packages:
      cmsearch_tblout_deoverlap:
        specs:
          - 'https://github.com/nawrockie/cmsearch_tblout_deoverlap'
        version:
          - '0.02'
  - class: DockerRequirement
    dockerPull: biocrusoe/cmsearch-deoverlap
  - class: gx:interface
    gx:inputs:
      - gx:name: clan_information
        gx:type: data
        gx:format: 'txt'
        gx:optional: True
      - gx:name: cmsearch_matches
        gx:type: data
        gx:format: 'txt'
$schemas:
  - 'http://edamontology.org/EDAM_1.16.owl'
  - 'https://schema.org/version/latest/schema.rdf'
s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2017"
s:author: "Michael Crusoe, Maxim Scheremetjew"