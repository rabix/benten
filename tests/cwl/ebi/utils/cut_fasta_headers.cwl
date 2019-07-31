#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool

label: Cuts FASTA headers which are too long
doc: >-
  Cuts away everything after the first whitespace character.

# TODO: Base command does not seem to work with cwl-runner
baseCommand: [ cut, -d , '" "', -f1 ]

inputs:
  fastaFile:
    type: File
    streamable: true
    format: edam:format_1929  # FASTA

stdout: $(inputs.fastaFile.nameroot).cut.fasta

outputs:
  sequences_with_cutted_headers:
    type: stdout
    format: edam:format_1929  # FASTA

arguments:
  - position: 0
    shellQuote: false
    valueFrom: $(inputs.fastaFile.path)

hints:
  - class: DockerRequirement
    dockerPull: 'alpine:3.7'

$namespaces:
 edam: http://edamontology.org/
 s: http://schema.org/
$schemas:
 - http://edamontology.org/EDAM_1.16.owl
 - https://schema.org/docs/schema_org_rdfa.html

s:license: "https://www.apache.org/licenses/LICENSE-2.0"
s:copyrightHolder: "EMBL - European Bioinformatics Institute, 2018"