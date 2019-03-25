var cwl_snippets = [
{
name: "CLT",
tabTrigger: "clt",
content:
`class: CommandLineTool
cwlVersion: v1.0
doc: ''
id: test
label: test
inputs: []
outputs: []
baseCommand: ''
hints: []
requirements: []
`
},
{
name: "ET",
tabTrigger: "et",
content:
`class: ExpressionTool
cwlVersion: v1.0
id: ''
label: ''
doc: ''
expression: '$\{
    // Expression
    \}'
inputs: []
outputs: []
hints: []
requirements:
  - class: InlineJavascriptRequirement
`
},
{
name: "WF",
tabTrigger: "wf",
content:
`class: Workflow
cwlVersion: v1.0
doc: ''
id: test
label: test
inputs: []
outputs: []
steps: []
requirements: []
hints: []
`
}

]
