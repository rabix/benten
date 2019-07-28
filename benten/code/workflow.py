"""Code to parse step interfaces and connectivity and present results in
a generic way that can be used by code intelligence as well as graph
drawing routines.

We try and be parsimonious about our parsing. On the first pass through,
when we analyze all CWL types, we parse all the individual steps with
this code. We keep references to all the steps in a separate
structure.

In the end we do a global analysis of the workflow, flagging connectivity
problems and building a graph of the workflow. We use this global analysis
to enable port completion. For all of this we reuse the previously extracted
step information.
"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
from dataclasses import dataclass
from typing import Dict

from ..cwl.lib import (check_linked_file, get_range_for_key,
                       get_range_for_value, list_as_map, ListOrMap)
from .yaml import fast_load
from .intelligence import IntelligenceNode, IntelligenceContext
from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity


# TODO: Use typed objects for ports to check types
class StepInterface:
    def __init__(self, inputs=None, outputs=None):
        self.inputs = inputs or set()
        self.outputs = outputs or set()


class Workflow(IntelligenceContext):
    def __init__(self):
        self.step_intels: Dict[str, WFStepIntelligence] = {}
        self.wf_inputs = []
        self.wf_outputs = []

    def analyze_connections(self, steps: ListOrMap, problems):
        for step_id, step in steps.as_dict.items():
            pass

    def get_step_intel(self, step_id):
        return self.step_intels.get(step_id)

    def get_output_source_completer(self):
        return WFOutputSourceCompleter(self)


class WFOutputSourceCompleter(IntelligenceNode):
    def __init__(self, workflow: Workflow):
        super().__init__()
        self.workflow = workflow

    def completion(self):
        step_ports = [f"{step_id}/{port}"
                      for step_id, step_intel in self.workflow.step_intels.items()
                      for port in step_intel.step_interface.outputs]
        return set(step_ports + self.workflow.wf_inputs)


class WFStepIntelligence(IntelligenceContext):
    def __init__(self, step_id, step_interface: StepInterface):
        super().__init__()
        self.step_id = step_id
        self.step_interface = step_interface
        self.workflow = None

    def validate_connections(self, inputs: ListOrMap, problems):
        if self.workflow is None:
            raise RuntimeError("Need to attach workflow first")

        for port_id, port in inputs.as_dict.items():
            if port_id not in self.step_interface.inputs:
                problems += [
                    Diagnostic(
                        _range=inputs.get_range_for_id(port_id),
                        message=f"Expecting one of: {self.step_interface.inputs}",
                        severity=DiagnosticSeverity.Error)
                ]

            else:
                if isinstance(port, str):
                    src = port
                elif isinstance(port, dict):
                    src = port.get("source")
                else:
                    continue

                if src in self.workflow.wf_inputs:
                    continue

                if "/" in src:
                    src_step, src_port = src.split("/")
                    if src_step != self.step_id:
                        if src_step in self.workflow.step_intels:
                            if src_port in self.workflow.step_intels[src_step].outputs:
                                continue

                problems += [
                    Diagnostic(
                        _range=inputs.get_range_for_id(port_id),
                        message=f"Port has invalid source",
                        severity=DiagnosticSeverity.Error)
                ]

    def get_step_inport_completer(self):
        return WFStepInputPortCompleter(inputs=self.step_interface.inputs)

    def get_step_output_completer(self):
        return WFStepOutputPortCompleter(outputs=self.step_interface.outputs)

    def get_step_source_completer(self):
        return PortSourceCompleter(self)


class WFStepInputPortCompleter(IntelligenceNode):
    def __init__(self, inputs):
        super().__init__(completions=inputs)


class WFStepOutputPortCompleter(IntelligenceNode):
    def __init__(self, outputs):
        super().__init__(completions=outputs)


class PortSourceCompleter(IntelligenceNode):
    def __init__(self, step_intel: WFStepIntelligence):
        super().__init__()
        self.step_intel = step_intel

    def completion(self):
        step_ports = [f"{step_id}/{port}"
                      for step_id, step_intel in self.step_intel.workflow.step_intels.items()
                      if step_id != self.step_intel.step_id
                      for port in step_intel.step_interface.outputs]
        return set(step_ports + self.step_intel.workflow.wf_inputs)


# This should be invoked when we arrive at the "run" field of a workflow
def parse_step_interface(doc_uri, step, problems):

    run_field = step.get("run")
    step_interface = StepInterface()
    linked_file = None

    if isinstance(run_field, str):
        linked_file = check_linked_file(doc_uri, run_field, step.lc.value("run"), problems)
        if linked_file is not None:
            run_field = fast_load.load(linked_file)

    if isinstance(run_field, dict):
        step_interface = StepInterface(
            inputs=set(list_as_map(run_field.get("inputs"),
                                   key_field="id",
                                   problems=problems).keys()),
            outputs=set(list_as_map(run_field.get("outputs"),
                                    key_field="id",
                                    problems=problems).keys()))

    return linked_file, step_interface
