# This is a valid workflow and will parse properly
# But since neither the parent nor nested document
# have ids, Benten will refuse to open the sub-workflow
# and should present a warning message

class: Workflow
inputs:
  a: File
  b: string
outputs:
  a:
    outputSource: s1/d
steps:
  s1:
    in:
       c: a
       b: b
    out:
       d: File
    run:
       class: CommandLineTool
       inputs:
         c: File
         b: string
       outputs:
         d: string
