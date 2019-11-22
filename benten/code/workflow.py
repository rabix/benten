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

from typing import Dict

from ..cwl.lib import (get_range_for_value, list_as_map, ListOrMap)
from .intelligence import IntelligenceNode, CompletionItem
from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity


import logging
logger = logging.getLogger(__name__)


# TODO: Use typed objects for ports to check types
class StepInterface:
    def __init__(self, inputs=None, outputs=None):
        self.inputs = inputs or set()
        self.outputs = outputs or set()


class Workflow:
    def __init__(self, inputs, outputs, steps):
        self._inputs = inputs
        self._outputs = outputs
        self._steps = steps

        self.step_intels: Dict[str, WFStepIntelligence] = {}
        self.wf_inputs = set(list_as_map(inputs, key_field="id", problems=[]).keys())
        self.wf_outputs = set(list_as_map(outputs, key_field="id", problems=[]).keys())

    def validate_connections(self, problems):
        unused_ports = set(self.wf_inputs)
        self.validate_step_connections(unused_ports, problems)
        self.validate_outputs(unused_ports, problems)
        self.flag_unused_inputs(unused_ports, problems)

    def validate_outputs(self, unused_ports, problems):
        outputs = ListOrMap(self._outputs, key_field="id", problems=[])
        for output_id, output in outputs.as_dict.items():
            _validate_source(
                port=output,
                src_key="outputSource",
                value_range=outputs.get_range_for_value(output_id),
                step_id=None,
                workflow=self,
                unused_ports=unused_ports,
                problems=problems)

    def validate_step_connections(self, unused_ports, problems):
        _steps = ListOrMap(self._steps, key_field="id", problems=[])
        for step_id, step in _steps.as_dict.items():
            step_intel = self.step_intels.get(step_id)
            if step_intel and isinstance(step, dict):
                step_intel.validate_connections(
                    ListOrMap(step.get("in"), key_field="id", problems=[]),
                    unused_ports=unused_ports,
                    problems=problems)

    def flag_unused_inputs(self, unused_ports, problems):
        inputs = ListOrMap(self._inputs, key_field="id", problems=[])
        for inp in unused_ports:
            if inp in inputs.as_dict:
                problems += [
                    Diagnostic(
                        _range=inputs.get_range_for_id(inp),
                        message=f"Unused input",
                        severity=DiagnosticSeverity.Warning)
                ]

    def add_step_intel(self, step_id, step_intel: 'WFStepIntelligence'):
        step_intel.workflow = self
        self.step_intels[step_id] = step_intel

    def get_step_intel(self, step_id):
        return self.step_intels.get(step_id)

    def get_output_source_completer(self, prefix):
        return WFOutputSourceCompleter(self, prefix)


class WFStepIntelligence:
    def __init__(self, step_id):
        super().__init__()
        self.step_id = step_id
        self.step_interface: StepInterface = StepInterface()
        self.workflow = None

    def set_step_interface(self, step_interface: StepInterface):
        self.step_interface = step_interface

    def validate_connections(self, inputs: ListOrMap, unused_ports, problems):
        if self.workflow is None:
            raise RuntimeError("Need to attach workflow first")

        for port_id, port in inputs.as_dict.items():
            if port_id not in self.step_interface.inputs:
                problems += [
                    Diagnostic(
                        _range=inputs.get_range_for_id(port_id),
                        message=
                        f"Expecting one of: {self.step_interface.inputs}"
                        if self.step_interface.inputs else
                        "No input ports found for this step",
                        severity=DiagnosticSeverity.Error)
                ]

            else:
                _validate_source(
                    port=port,
                    src_key="source",
                    value_range=inputs.get_range_for_value(port_id),
                    step_id=self.step_id,
                    workflow=self.workflow,
                    unused_ports=unused_ports,
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


class PortSourceCompleterBase(IntelligenceNode):
    def __init__(self, prefix):
        super().__init__()
        self.prefix = prefix

    def _completion(self, workflow, step_id=None):
        if "/" not in self.prefix:
            return [
                CompletionItem(label=_id)
                for _port in (workflow.step_intels.keys(), workflow.wf_inputs)
                for _id in _port
                if _id != step_id
            ]
        else:
            src_step, src_port = self.prefix.split("/")
            step_intel = workflow.step_intels.get(src_step)
            if step_intel is not None:
                return [
                    CompletionItem(label=_id)
                    for _id in step_intel.step_interface.outputs
                ]


class PortSourceCompleter(PortSourceCompleterBase):
    def __init__(self, step_intel: WFStepIntelligence, prefix):
        super().__init__(prefix)
        self.step_intel = step_intel

    def completion(self):
        return self._completion(workflow=self.step_intel.workflow, step_id=self.step_intel.step_id)


class WFOutputSourceCompleter(PortSourceCompleterBase):
    def __init__(self, workflow: Workflow, prefix):
        super().__init__(prefix)
        self.workflow = workflow

    def completion(self):
        return self._completion(workflow=self.workflow)


# This should be invoked when we arrive at the "run" field of a workflow
def parse_step_interface(run_field: dict, problems: list):

    step_interface = StepInterface()

    if isinstance(run_field, dict):
        step_interface = StepInterface(
            inputs=set(list_as_map(run_field.get("inputs"),
                                   key_field="id",
                                   problems=problems).keys()),
            outputs=set(list_as_map(run_field.get("outputs"),
                                    key_field="id",
                                    problems=problems).keys()))

    return step_interface


def _validate_source(port, src_key, value_range, step_id, workflow, unused_ports, problems):

    src = None
    if isinstance(port, (str, list)):
        src = port
    elif isinstance(port, dict):
        if src_key in port:
            src = port.get(src_key)
            value_range = get_range_for_value(port, src_key)

    if src is None:
        return

    if isinstance(src, list):
        for n, _src in enumerate(src):
            _validate_one_source(_src, get_range_for_value(src, n), step_id, workflow, unused_ports, problems)
    elif isinstance(src, str):
        _validate_one_source(src, value_range, step_id, workflow, unused_ports, problems)


def _validate_one_source(src, value_range, step_id, workflow, unused_ports, problems):

    if src is None:
        return

    unused_ports.discard(src)

    if src in workflow.wf_inputs:
        return

    err_msg = f"No such workflow input. Expecting one of {workflow.wf_inputs}"

    if isinstance(src, str) and "/" in src:
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
