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
from .intelligence import IntelligenceNode, IntelligenceContext, CompletionItem
from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity


import logging
logger = logging.getLogger(__name__)


# TODO: Use typed objects for ports to check types
class StepInterface:
    def __init__(self, inputs=None, outputs=None):
        self.inputs = inputs or set()
        self.outputs = outputs or set()


class Workflow(IntelligenceContext):
    def __init__(self, inputs, outputs):
        self.step_intels: Dict[str, WFStepIntelligence] = {}
        self.wf_inputs = set(list_as_map(inputs, key_field="id", problems=[]).keys())
        self.wf_outputs = set(list_as_map(outputs, key_field="id", problems=[]).keys())
        self._output_node = outputs

    def validate_connections(self, steps, problems):
        self.validate_outputs(problems)

        _steps = ListOrMap(steps, key_field="id", problems=[])
        for step_id, step in _steps.as_dict.items():
            step_intel = self.step_intels.get(step_id)
            if step_intel:
                step_intel.validate_connections(
                    ListOrMap(step.get("in"), key_field="id", problems=[]),
                    problems=problems)

    def validate_outputs(self, problems):
        outputs = ListOrMap(self._output_node, key_field="id", problems=[])
        for output_id, output in outputs.as_dict.items():
            _validate_source(
                port=output,
                src_key="outputSource",
                value_range=outputs.get_range_for_value(output_id),
                step_id=None,
                workflow=self,
                problems=problems)

    def add_step_intel(self, step_id, step_intel: 'WFStepIntelligence'):
        step_intel.workflow = self
        self.step_intels[step_id] = step_intel

    def get_step_intel(self, step_id):
        return self.step_intels.get(step_id)

    def get_output_source_completer(self):
        return WFOutputSourceCompleter(self)


class WFOutputSourceCompleter(IntelligenceNode):
    def __init__(self, workflow: Workflow):
        super().__init__()
        self.workflow = workflow

    def completion(self):
        return [
            CompletionItem(label=l)
            for ll in (
                (f"{step_id}/{port}"
                 for step_id, step_intel in self.workflow.step_intels.items()
                 for port in step_intel.step_interface.outputs),
                self.workflow.wf_inputs)
            for l in ll
        ]


class WFStepIntelligence(IntelligenceContext):
    def __init__(self, step_id):
        super().__init__()
        self.step_id = step_id
        self.step_interface: StepInterface = StepInterface()
        self.workflow = None

    def set_step_interface(self, step_interface: StepInterface):
        self.step_interface = step_interface

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
                _validate_source(
                    port=port,
                    src_key="source",
                    value_range=inputs.get_range_for_value(port_id),
                    step_id=self.step_id,
                    workflow=self.workflow,
                    problems=problems)

    def get_step_inport_completer(self):
        return WFStepInputPortCompleter(inputs=self.step_interface.inputs)

    def get_step_output_completer(self):
        return WFStepOutputPortCompleter(outputs=self.step_interface.outputs)

    def get_step_source_completer(self, prefix):
        return PortSourceCompleter(self, prefix)


class WFStepInputPortCompleter(IntelligenceNode):
    def __init__(self, inputs):
        super().__init__(completions=inputs)


class WFStepOutputPortCompleter(IntelligenceNode):
    def __init__(self, outputs):
        super().__init__(completions=outputs)


class PortSourceCompleter(IntelligenceNode):
    def __init__(self, step_intel: WFStepIntelligence, prefix):
        super().__init__()
        self.step_intel = step_intel
        self.prefix = prefix

    def completion(self):
        if "/" not in self.prefix:
            return [
                CompletionItem(label=_id)
                for _port in (self.step_intel.workflow.step_intels.keys(),
                              self.step_intel.workflow.wf_inputs)
                for _id in _port
                if _id != self.step_intel.step_id
            ]
        else:
            src_step, src_port = self.prefix.split("/")
            step_intel = self.step_intel.workflow.step_intels.get(src_step)
            if step_intel is not None:
                return [
                    CompletionItem(label=_id)
                    for _id in step_intel.step_interface.outputs
                ]


# This should be invoked when we arrive at the "run" field of a workflow
def parse_step_interface(doc_uri, run_field, linked_file: pathlib.Path, problems):

    step_interface = StepInterface()

    if isinstance(run_field, str):
        if linked_file.exists() and linked_file.is_file():
            run_field = fast_load.load(linked_file)

    if isinstance(run_field, dict):
        step_interface = StepInterface(
            inputs=set(list_as_map(run_field.get("inputs"),
                                   key_field="id",
                                   problems=problems).keys()),
            outputs=set(list_as_map(run_field.get("outputs"),
                                    key_field="id",
                                    problems=problems).keys()))

    return step_interface


def _validate_source(port, src_key, value_range, step_id, workflow, problems):

    src = None
    if isinstance(port, str):
        src = port
    elif isinstance(port, dict):
        if src_key in port:
            src = port.get(src_key)
            value_range = get_range_for_value(port, src_key)

    if src is None:
        return

    if isinstance(src, list):
        for n, _src in enumerate(src):
            _validate_one_source(_src, get_range_for_value(src, n), step_id, workflow, problems)
    else:
        _validate_one_source(src, value_range, step_id, workflow, problems)


def _validate_one_source(src, value_range, step_id, workflow, problems):
    if src in workflow.wf_inputs:
        return

    err_msg = "No such workflow input"

    if "/" in src:
        src_step, src_port = src.split("/")
        err_msg = "Port can not connect to same step"
        if src_step != step_id:
            err_msg = f"No step called {src_step}"
            if src_step in workflow.step_intels:
                err_msg = f"{src_step} has no port called {src_port}"
                if src_port in workflow.step_intels[src_step].step_interface.outputs:
                    return

    problems += [
        Diagnostic(
            _range=value_range,
            message=err_msg,
            severity=DiagnosticSeverity.Error)
    ]
