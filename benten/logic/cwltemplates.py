"""Collection of CWL templates"""

wf_input_template = \
"""type:
default:
label:
format:
doc:
"""

wf_output_template = \
"""outputSource:
"""


wf_template = \
"""class: Workflow
cwlVersion: v1.0
id: new_wf
label: New workflow
inputs: []
outputs: []
steps: []
doc: Blessed by Benzaiten
"""

step_template = \
"""label: {step_id}
in: []
out: []
run: {run_path}
"""

