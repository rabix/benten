from typing import Dict, List
import time

from .lineloader import YNone, Ydict, load_cwl_resolve_lams
from ..langserver.lspobjects import (
    Diagnostic, DiagnosticSeverity, Range, Position, Location, DocumentSymbol, SymbolKind)
from .process import Base, resolve_file_path

import logging
logger = logging.getLogger(__name__)


# Very unlikely a user's id choice would unintentionally collide with these
special_id_for_inputs = "-:benteninputs:-"
special_id_for_outputs = "-:bentenoutputs:-"


# Not only the line number, but in the future we can type the port and do type
# checking for connections
class Port:
    def __init__(self, node_id: (None, str), port_id: str):
        self.node_id = node_id
        self.port_id = port_id

    def __eq__(self, other: 'Port'):
        return self.node_id == other.node_id and self.port_id == other.port_id


class Connection:
    def __init__(self, src: Port, dst: Port, line: (None, int) = None):
        self.line = line
        self.src = src
        self.dst = dst

    def __eq__(self, other: 'Connection'):
        return self.src == other.src and self.dst == other.dst


class StepInterface:
    def __init__(self, _id: str, step: (YNone, str, dict)):
        self.id = _id
        self.label = None
        self.available_inputs = {}
        self.available_outputs = {}

        if isinstance(step, YNone):
            return

        if isinstance(step, str):
            cwl = load_cwl_resolve_lams(step)
        else:
            cwl = step

        self.label = cwl.get("label")
        self.available_inputs = {k: Port(_id, k) for k in cwl.get("inputs", {}).keys()}
        self.available_outputs = {k: Port(_id, k) for k in cwl.get("outputs", {}).keys()}


class WFConnectionError(Exception):
    pass


class WorkflowStructure(Base):

    def __init__(self, *args, **kwargs):
        super(WorkflowStructure, self).__init__(*args, **kwargs)

        self._structure = {
            "inputs": {},
            "steps": {},
            "connections": [],
            "outputs": {}
        }
        t0 = time.time()
        self._parse_io()
        self._parse_step_interfaces()
        self._extract_connection_list()
        logger.debug(f"Parsed workflow structure in {time.time() - t0}s")

    def graph(self):
        return self._organize_hierarchy({
            "nodes": [
                {"id": k, "label": v.label}
                for k, v in self._structure["steps"].items()
            ] + [
                {"id": special_id_for_inputs, "label": "inputs"},
                {"id": special_id_for_outputs, "label": "outputs"}
            ],
            "edges": [
                (conn.src.node_id, conn.dst.node_id)
                for conn in self._structure["connections"]
            ]
        })

    def _parse_io(self):
        _inputs = self.ydict.get("inputs", {})
        if not isinstance(_inputs, dict):
            _inputs = {}
        self._structure["inputs"] = {
            k: Port(special_id_for_inputs, k)
            for k in _inputs.keys()
        }

        _outputs = self.ydict.get("outputs", {})
        if not isinstance(_outputs, dict):
            _outputs = {}
        self._structure["outputs"] = {
            k: Port(special_id_for_outputs, k)
            for k in _outputs.keys()
        }

    def _parse_step_interfaces(self):
        _steps = self.ydict.get("steps", {})
        if not isinstance(_steps, dict):
            _steps = {}

        step_structures = self._structure["steps"]
        for _id, _step in _steps.items():

            if not isinstance(_step, dict):
                continue

            _run = _step.get("run")
            if isinstance(_run, str):
                try:
                    step_structures[_id] = StepInterface(
                        _id,
                        resolve_file_path(self.doc_uri, _run).read_text())
                except FileNotFoundError:
                    self.problems += [
                        Diagnostic(
                            _range=Range(
                                start=Position(_run.start.line, 0),
                                end=Position(_run.end.line, _run.end.column)),
                            message=f"Missing linked file: {_run}",
                            severity=DiagnosticSeverity.Error,
                            code="CWL err",
                            source="Benten")]
                    continue
            elif isinstance(_run, dict):
                step_structures[_id] = StepInterface(_id, _run)
            else:
                self.problems += [
                    Diagnostic(
                        _range=Range(
                            start=Position(_run.start.line, 0),
                            end=Position(_run.end.line, _run.end.column)),
                        message=f"Step must be String or Process",
                        severity=DiagnosticSeverity.Error,
                        code="CWL err",
                        source="Benten")]
                continue

            if step_structures[_id].label is None:
                step_structures[_id].label = _id

    def _extract_connection_list(self):
        _connections = self._structure["connections"]

        _steps = self.ydict.get("steps", {})
        if not isinstance(_steps, dict):
            _steps = {}

        # todo: refactor and merge the step connection and output connection code
        for _id, _step in _steps.items():
            _step_interface: StepInterface = self._structure["steps"].get(_id)

            # This only validates the exposed outputs. Does not contribute to the connection list
            for _outp in _step.get("out", []):
                if _outp not in _step_interface.available_outputs:
                    self.problems += [
                        Diagnostic(
                            _range=Range(
                                start=Position(_outp.start.line, 0),
                                end=Position(_outp.start.line, 80)),
                            message=f"{_id} has no output port {_outp}.\n"
                            f"Available ports are {list(_step_interface.available_outputs.keys())}",
                            severity=DiagnosticSeverity.Error,
                            code="CWL err",
                            source="Benten")]

            for _port_id, _input in _step.get("in", {}).items():
                if isinstance(_input, (str, list)):
                    _src = _input
                elif isinstance(_input, dict):
                    _src = _input.get("source", [])
                else:
                    continue

                if isinstance(_src, list):
                    _src_v = _src
                elif isinstance(_src, str):
                    _src_v = [_src]
                else:
                    continue

                try:
                    sink = _step_interface.available_inputs[_port_id]
                except KeyError:
                    self.problems += [
                        Diagnostic(
                            _range=Range(
                                start=Position(_input.start.line, 0),
                                end=Position(_input.start.line, 80)),
                            message=f"{_id} has no input port {_port_id}.\n"
                            f"Available ports are {list(_step_interface.available_inputs.keys())}",
                            severity=DiagnosticSeverity.Error,
                            code="CWL err",
                            source="Benten")]
                    continue

                for _conn in _src_v:
                    try:
                        source = self._get_source(_conn)
                    except WFConnectionError as e:
                        self.problems += [
                            Diagnostic(
                                _range=Range(
                                    start=Position(_conn.start.line, 0),
                                    end=Position(_conn.end.line, _conn.end.column)),
                                message=str(e),
                                severity=DiagnosticSeverity.Error,
                                code="CWL err",
                                source="Benten")]
                        continue
                    _connections += [Connection(source, sink)]

        _outputs = self.ydict.get("outputs", {})
        if not isinstance(_outputs, dict):
            _outputs = {}

        for _id, _out in _outputs.items():
            # _step_interface: StepInterface = self._structure["steps"].get(_id)
            if isinstance(_out, (str, list)):
                _dst = _out
            elif isinstance(_out, dict):
                _dst = _out.get("outputSource", [])
            else:
                continue

            if isinstance(_dst, list):
                _dst_v = _dst
            elif isinstance(_dst, str):
                _dst_v = [_dst]
            else:
                continue

            sink = self._structure["outputs"].get(_id)
            for _conn in _dst_v:
                try:
                    source = self._get_source(_conn)
                except WFConnectionError as e:
                    self.problems += [
                        Diagnostic(
                            _range=Range(
                                start=Position(_conn.start.line, 0),
                                end=Position(_conn.end.line, _conn.end.column)),
                            message=str(e),
                            severity=DiagnosticSeverity.Error,
                            code="CWL err",
                            source="Benten")]
                    continue
                _connections += [Connection(source, sink)]

    def _get_source(self, _conn) -> (None, Port):

        if isinstance(_conn, YNone) or _conn == "":
            return None

        if "/" in _conn:
            return self._get_step_source(_conn)
        else:
            return self._structure.get("inputs", {}).get(_conn)

    def _get_step_source(self, _conn) -> Port:
        src_step_id, src_port_id = _conn.split("/")

        if src_step_id not in self._structure["steps"]:
            raise WFConnectionError("No such source step {}".format(src_step_id))

        if src_port_id not in self._structure["steps"][src_step_id].available_outputs:
            raise WFConnectionError("No such source port {}.{}".format(src_step_id, src_port_id))

        return self._structure["steps"][src_step_id].available_outputs[src_port_id]

    @staticmethod
    def _organize_hierarchy(graph):

        nodes = {n["id"]: n for n in graph["nodes"]}
        for v in nodes.values():
            v["level"] = 0

        keys = [special_id_for_inputs] + [k for k in nodes.keys() if k != special_id_for_inputs]

        for k in keys:
            node = nodes[k]
            for conn in graph["edges"]:
                if conn[0] == node["id"]:
                    nodes[conn[1]]["level"] = \
                        max(nodes[conn[1]]["level"], node["level"] + 1)

        return graph
