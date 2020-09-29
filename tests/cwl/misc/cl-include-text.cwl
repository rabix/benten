#!/usr/bin/env cwl-runner
class: CommandLineTool
cwlVersion: v1.0

requirements:
  InitialWorkDirRequirement:
    listing:
    - entryname: text1.txt
      entry:
        $include: text1.txt

inputs:
  one:
    type: string

outputs:
  output:
    type: stdout
stdout: text1.out

baseCommand:
- cat
- text1.txt
