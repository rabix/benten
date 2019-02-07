"""This model should allow us to perform the following operations on a CWL document
that is a workflow:

Line number operations
1. Return line range for a step so we can highlight the start line or delete the step
2. Return line range for a connection so we can highlight it, or delete it
3. Return range for a workflow input/output so we can highlight it, create it, delete it
4. Find the last line of the "steps" section so we can append a step to it.

Listing operations
1. List all inputs, outputs and steps of a workflow
2. List all inputs/outputs of a workflow
3. List all possible inputs and outputs for a step

Edit operations:
Consists of a line number (range), text to insert, and final cursor position.
A delete is line number range and empty text.
A replace is a line number range and some text.
An insert is a single line number and some text.
An edit operation can consist of multiple non local operations

1. Delete a step
2. Insert a step with basic fields filled out (tell us line number to insert at, and raw CWL)
3. Delete a connection
4. insert a connection
5. Add/remove a workflow input/output

"""
import pathlib
from collections import OrderedDict
import logging

from ruamel.yaml.comments import CommentedMap

import benten.lib as blib


logger = logging.getLogger(__name__)


# class Section:
#     def __init__(self, line: int, contents: dict):
#         self.line = line
#         self.contents = contents
#
#     def __contains__(self, item):
#         return item in self.contents
#
#     def __getitem__(self, item):
#         return self.contents[item]


# Not only the line number, but in the future we can type the port and do type
# checking for connections
class Port:
    def __init__(self, node_id: (None, str), port_id: str, line: (None, int)=None):
        self.node_id = node_id
        self.port_id = port_id
        self.line = line

    def __eq__(self, other: 'Port'):
        return self.node_id == other.node_id and self.port_id == other.port_id

    def __repr__(self):
        if self.node_id is not None:
            return "{}.{}".format(self.node_id, self.port_id)
        else:
            return self.port_id


class Step:
    def __init__(self, _id: str, line: int,
                 sinks: 'OrderedDict[str, Port]',
                 sources: 'OrderedDict[str, Port]'):
        self.line = line
        self.id = _id
        self.available_sinks = sinks
        self.available_sources = sources

    def __repr__(self):
        return str(self.available_sinks.keys()) + "->" + self.id + "->" + str(self.available_sources.keys())

    @classmethod
    def from_doc(cls, step_id: str, line: int, step_doc: CommentedMap, root: pathlib.Path):
        if step_doc is None or "run" not in step_doc:
            sinks = {}
            sources = {}
        else:
            if isinstance(step_doc["run"], str):
                sub_process = blib.load_cwl(
                    pathlib.Path(root, step_doc["run"]).resolve().as_uri(),
                    round_trip=False)
            else:
                sub_process = step_doc["run"]

            sinks = OrderedDict([
                (k, Port(node_id=step_id, port_id=k))
                for k, v in blib.iter_over_plain_lom(sub_process.get("inputs", {}))
            ])

            sources = OrderedDict([
                (k, Port(node_id=step_id, port_id=k))
                for k, v in blib.iter_over_plain_lom(sub_process.get("outputs", {}))
            ])

        return cls(_id=step_id, line=line, sinks=sinks, sources=sources)


class Connection:
    def __init__(self, src: Port, dst: Port, line: (None, int)):
        self.line = line
        self.src = src
        self.dst = dst

    def __eq__(self, other: 'Connection'):
        return self.src == other.src and self.dst == other.dst

    def __repr__(self):
        return "{} -> {}".format(self.src, self.dst)


class WFConnectionError(Exception):
    pass


class Workflow:
    """This object carries the raw YAML and some housekeeping datastructures"""

    def __init__(self, cwl_doc: CommentedMap, path: pathlib.Path):
        self.cwl_doc = cwl_doc or {}
        self.file_path = path
        self.problems_with_wf = []

        required_sections = ["cwlVersion", "class", "inputs", "outputs", "steps"]
        for sec in required_sections:
            if sec not in self.cwl_doc:
                self.problems_with_wf += ["'{}' missing".format(sec)]

        self.inputs = OrderedDict([
            (k, Port(node_id=None, port_id=k, line=l))
            for k, v, l in blib.iter_over_lom(self.cwl_doc.get("inputs", {}))
        ])

        self.outputs = OrderedDict([
            (k, Port(node_id=None, port_id=k, line=l))
            for k, v, l in blib.iter_over_lom(self.cwl_doc.get("outputs", {}))
        ])

        self.steps = OrderedDict(
            (k, Step.from_doc(step_id=k, line=l, step_doc=v, root=self.file_path.parent))
            for k, v, l in blib.iter_over_lom(self.cwl_doc.get("steps", {}))
        )

        self.connections = self._list_connections()

    def _get_source(self, _src) -> Port:
        if _src is None or _src == "":
            raise WFConnectionError("No source specified")

        if "/" in _src:
            return self._get_step_source(_src)
        else:
            if _src not in self.inputs:
                raise WFConnectionError("No such WF input {}".format(_src))
            return self.inputs[_src]

    def _get_step_source(self, _src) -> Port:
        src_step_id, src_port_id = _src.split("/")

        if src_step_id not in self.steps:
            raise WFConnectionError("No such source step {}".format(src_step_id))

        if src_port_id not in self.steps[src_step_id].available_sources:
            raise WFConnectionError("No such source port {}.{}".format(src_step_id, src_port_id))

        return self.steps[src_step_id].available_sources[src_port_id]

    def _list_connections(self) -> [Connection]:

        connections = []
        # Some things are better to write with old fashioned loops rather than
        # list comprehensions ...

        # Connections into steps
        for step_id, step_doc, _ in blib.iter_over_lom(self.cwl_doc.get("steps", {})):
            if not isinstance(step_doc, dict):
                self.problems_with_wf += ["Invalid step: {}".format(step_id)]
                continue

            this_step: Step = self.steps[step_id]
            # TODO: error check
            for step_sink_id, port_doc, _ in blib.iter_over_lom(step_doc.get("in", {})):
                sink = this_step.available_sinks.get(step_sink_id, None)
                if sink is None:
                    self.problems_with_wf += ["No such sink: {}.{}".format(this_step.id, step_sink_id)]
                    continue

                if "source" not in port_doc:
                    # Ignore default values for now
                    continue

                ln_no = port_doc.lc.value("source")[0]
                for n, _src in enumerate(blib.listify(port_doc["source"])):
                    try:
                        source = self._get_source(_src)
                        connections.append(Connection(source, sink, ln_no + n))
                    except WFConnectionError as e:
                        self.problems_with_wf += ["{}.{}: {}".format(this_step, step_sink_id, e)]
                        continue

        # Connections to WF outputs
        for out_id, out_doc, l in blib.iter_over_lom(self.cwl_doc.get("outputs", {})):
            sink = self.outputs[out_id]

            if "outputSource" in blib.lom(out_doc):
                ln_no = out_doc.lc.value("outputSource")[0]
                for n, _src in enumerate(blib.listify(out_doc["outputSource"])):
                    try:
                        source = self._get_source(_src)
                        connections.append(Connection(source, sink, ln_no + n))
                    except WFConnectionError as e:
                        self.problems_with_wf += ["{}: {}".format(sink.port_id, e)]
                        continue

        return connections

    def find_connection(self, conn: Connection) -> (int, None):
        for existing_conn in self.connections:
            if existing_conn == conn:
                return existing_conn.line
        else:
            return None

    def to_string(self):
        return blib.cwl_raw_text(self.cwl_doc)
