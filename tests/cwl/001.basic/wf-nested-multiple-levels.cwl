
class: Workflow
inputs:
  a: File
  b: string
outputs:
  a:
    outputSource: [s1/d, s2/d]
steps:

  s1:
    in:
       c: a
    out:
       d: File
    run:
       class: CommandLineTool
       inputs:
         c: File
       outputs:
         d: File

  s2:
    in:
       b: b
    out:
       d: File
    run:
        class: Workflow
        inputs:
          a: File
        outputs:
          a:
            outputSource: s1/d
        steps:

          s1:
            in:
               c: a
            out:
               d: File
            run:
               class: CommandLineTool
               inputs:
                 c: File
               outputs:
                 d: File
