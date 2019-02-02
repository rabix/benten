import pathlib

import benten


default_templates = {

    "CommandlineTool": {
        "doc": "A Command Line Tool is a non-interactive executable program that reads some input, performs a computation, and terminates after producing some output.",
        "file": "commandlinetool.cwl",
        "cwl": \
"""class: CommandLineTool
cwlVersion: v1.0
id: 
label:
doc:
baseCommand:
arguments:
inputs: []
outputs: []
stdin:
stderr:
stdout:
requirements: []
hints: []
successCodes: []
temporaryFailCodes: []
permanentFailCodes: []"""
    },

    "ExpressionTool": {
        "doc": "Execute an expression as a Workflow step",
        "file": "expressiontool.cwl",
        "cwl": \
"""class: ExpressionTool
cwlVersion: v1.0
id:
label:
doc:
expression:
inputs: []
outputs: []
requirements: []
hints: []""",
    },

    "Workflow": {
        "doc": "A workflow describes a set of steps and the dependencies between those steps",
        "file": "workflow.cwl",
        "cwl":
"""class: Workflow
cwlVersion: v1.0
id:
label:
doc:
inputs: []
outputs: []
steps: []
requirements: []
hints: []"""
    }
}


def copy_cwl_templates_to_config_directory_as_needed():
    for label, data in default_templates.items():
        fpath = pathlib.Path(benten.template_dir, data["file"])
        if fpath.exists():
            continue
        else:
            with open(fpath, "w") as f:
                f.write(data["cwl"])
