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
from typing import List, Tuple
import pathlib
from collections import OrderedDict
import logging

from .base import (DocumentProblem, EditMark, Base, YamlView,
                   special_id_for_inputs, special_id_for_outputs, special_ids_for_io)
from ..editing.utils import dictify, iter_scalar_or_list
from ..editing.lineloader import load_yaml, YNone, Ydict, LAM
from .workfloweditmixin import WorkflowEditMixin


logger = logging.getLogger(__name__)


# Not only the line number, but in the future we can type the port and do type
# checking for connections
class Port:
    def __init__(self, node_id: (None, str), port_id: str, line: (None, (int, int))=None):
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


class InvalidSub:
    def __init__(self):
        self.id = None

    @staticmethod
    def type_str():
        return "has errors"


class InlineSub:
    def __init__(self, _id: str, inline_path: Tuple[str, ...]):
        self.id = _id
        self.inline_path = inline_path

    @staticmethod
    def type_str():
        return "Inline"


class ExternalSub:
    def __init__(self, _id: str, path: pathlib.Path):
        self.id = _id
        self.path = path

    @staticmethod
    def type_str():
        return "Linked"


class Step:
    def __init__(self, _id: str, line: (int, int),
                 sinks: 'OrderedDict[str, Port]',
                 sources: 'OrderedDict[str, Port]',
                 process_type: str,
                 sub_workflow: (InvalidSub, InlineSub, ExternalSub)):
        self.line = line
        self.id = _id
        self.available_sinks = sinks
        self.available_sources = sources
        self.process_type = process_type  # as returned by cwl_doc.process_type()
        self.sub_workflow = sub_workflow

    def about(self):
        return {
            "type": self.process_type,
            "step-type": self.sub_workflow.type_str()
        }

    def __repr__(self):
        return str(self.available_sinks.keys()) + "->" + self.id + "->" + str(self.available_sources.keys())

    @classmethod
    def from_doc(cls, step_id: str, line: (int, int), cwl_doc: YamlView, wf_error_list: List):

        step_doc = cwl_doc.yaml["steps"][step_id]
        root = pathlib.Path(cwl_doc.root().file_path)
        sub_workflow = InvalidSub()

        if isinstance(step_doc, (YNone, str)) or "run" not in step_doc:
            sinks = {}
            sources = {}
            sub_process = {}
            wf_error_list += [
                DocumentProblem(line=step_doc.start.line, column=step_doc.start.column,
                                message="step {} has no run field".format(step_id),
                                problem_type=DocumentProblem.Type.error,
                                problem_class=DocumentProblem.Class.cwl)]
        else:
            if isinstance(step_doc["run"], str):
                sub_p_path = pathlib.Path(root.parent, step_doc["run"]).resolve()
                try:
                    sub_process = load_yaml(sub_p_path.open("r").read())
                    sub_workflow = ExternalSub(_id=sub_process.get("id", None), path=sub_p_path)
                except FileNotFoundError:
                    sub_process = {}
                    wf_error_list += [
                        DocumentProblem(
                            line=step_doc.start.line, column=step_doc.start.column,
                            message="Could not find sub workflow: {} (resolved to {})".format(
                                step_doc["run"], sub_p_path.as_uri()),
                            problem_type=DocumentProblem.Type.error,
                            problem_class=DocumentProblem.Class.cwl)]
                    sub_workflow = InvalidSub()
            else:
                sub_process = step_doc["run"]
                if isinstance(sub_process, dict):
                    sub_workflow = InlineSub(
                        _id=sub_process.get("id", None), inline_path=("steps", step_id, "run"))
                else:
                    sub_process = {}
                    wf_error_list += [
                        DocumentProblem(
                            line=step_doc["run"].start.line, column=step_doc["run"].start.column,
                            message="Sub workflow is empty",
                            problem_type=DocumentProblem.Type.error,
                            problem_class=DocumentProblem.Class.cwl)]
                    sub_workflow = InvalidSub()

            sinks = OrderedDict([
                (k, Port(node_id=step_id, port_id=k))
                for k, v in dictify(sub_process.get("inputs", {})).items()
            ])

            sources = OrderedDict([
                (k, Port(node_id=step_id, port_id=k))
                for k, v in dictify(sub_process.get("outputs", {})).items()
            ])

        return cls(_id=step_id, line=line, sinks=sinks, sources=sources,
                   process_type=sub_process.get("class", "invalid"),
                   sub_workflow=sub_workflow)


class Connection:
    def __init__(self, src: Port, dst: Port, line: (None, (int, int))):
        self.line = line
        self.src = src
        self.dst = dst

    def __eq__(self, other: 'Connection'):
        return self.src == other.src and self.dst == other.dst

    def __repr__(self):
        return "{} -> {}".format(self.src, self.dst)


class WFConnectionError(Exception):
    pass


class Workflow(WorkflowEditMixin, Base):
    """This object carries the raw YAML and some housekeeping datastructures"""

    def __init__(self, cwl_doc: YamlView):
        super().__init__(cwl_doc=cwl_doc)
        self.id = (self.cwl_doc.yaml or {}).get("id", None)

        required_sections = ["cwlVersion", "class", "inputs", "outputs", "steps"]
        self.parse_sections(required_sections)

        cwl_dict = self.cwl_doc.yaml
        self.inputs = self._parse_ports(cwl_dict.get("inputs", {}))
        self.outputs = self._parse_ports(cwl_dict.get("outputs", {}))
        self.steps = {}
        self.connections = []

        if "steps" not in cwl_dict:
            self.cwl_errors += [DocumentProblem(line=0, column=0, message="Steps missing",
                                                problem_type=DocumentProblem.Type.error,
                                                problem_class=DocumentProblem.Class.cwl)]
        elif not isinstance(cwl_dict["steps"], (Ydict, LAM)):
            self.cwl_errors += [DocumentProblem(line=0, column=0,
                                                message="Steps need to be dictionary or list",
                                                problem_type=DocumentProblem.Type.error,
                                                problem_class=DocumentProblem.Class.cwl)]
        else:
            self.steps = OrderedDict(
                (k, Step.from_doc(
                    step_id=k, line=(v.start.line, v.end.line), cwl_doc=cwl_doc,
                    wf_error_list=self.cwl_errors))
                for k, v in cwl_dict.get("steps", {}).items()
            )
            self.connections = self._list_connections()

    @staticmethod
    def _parse_ports(obj):
        # Papers please
        # def _line_no(_v, _default: (int, int)):
        #     if isinstance(_v, (CWLList, CWLMap)):
        #         return _v.start.line, _v.end.line
        #     else:
        #         return _default
        #
        # if isinstance(obj, (CWLList, CWLMap)):
        #     def_ln = (obj.start.line, obj.end.line)
        # else:
        #     def_ln = None

        return OrderedDict([
            (k, Port(node_id=None, port_id=k, line=(v.start.line, v.end.line)))
            for k, v in obj.items()
        ])

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

        cwl_dict = self.cwl_doc.yaml

        # Connections into steps
        for step_id, step_doc in cwl_dict.get("steps", {}).items():
            if not isinstance(step_doc, dict):
                self.cwl_errors += [
                    DocumentProblem(line=step_doc.start.line, column=step_doc.start.column,
                                    message="Invalid step: {}".format(step_id),
                                    problem_type=DocumentProblem.Type.error,
                                    problem_class=DocumentProblem.Class.cwl)]
                continue

            this_step: Step = self.steps[step_id]
            # TODO: error check
            for step_sink_id, port_doc in (step_doc.get("in") or {}).items():
                sink = this_step.available_sinks.get(step_sink_id, None)
                if sink is None:
                    self.cwl_errors += [
                        DocumentProblem(line=port_doc.start.line, column=port_doc.start.column,
                                        message="No such sink: {}.{}".format(this_step.id, step_sink_id),
                                        problem_type=DocumentProblem.Type.error,
                                        problem_class=DocumentProblem.Class.cwl)]
                    continue

                if isinstance(port_doc, (str, list)):
                    port_src = port_doc
                elif isinstance(port_doc, dict):
                    if "source" in port_doc:
                        port_src = port_doc["source"]
                    else:
                        # Ignore default values for now
                        continue
                else:
                    self.cwl_errors += [
                        DocumentProblem(line=port_doc.start.line, column=port_doc.start.column,
                                        message="Can't parse source for {}.{}".format(this_step, step_sink_id),
                                        problem_type=DocumentProblem.Type.error,
                                        problem_class=DocumentProblem.Class.cwl)]
                    continue

                for _src in iter_scalar_or_list(port_src):
                    try:
                        source = self._get_source(_src)
                        connections.append(Connection(source, sink, (_src.start.line, _src.end.line)))
                    except WFConnectionError as e:
                        self.cwl_errors += [
                            DocumentProblem(line=_src.start.line, column=_src.start.column,
                                            message="{}.{}: {}".format(this_step, step_sink_id, e),
                                            problem_type=DocumentProblem.Type.error,
                                            problem_class=DocumentProblem.Class.cwl)]
                        continue

        # Connections to WF outputs
        for out_id, out_doc in (cwl_dict.get("outputs") or {}).items():
            sink = self.outputs[out_id]

            if "outputSource" in out_doc:
                # todo: figure out line numbers
                # ln_no = out_doc.lc.value("outputSource")[0]
                for _src in iter_scalar_or_list(out_doc["outputSource"]):
                    try:
                        source = self._get_source(_src)
                        connections.append(Connection(source, sink, (_src.start.line, _src.end.line)))
                    except WFConnectionError as e:
                        self.cwl_errors += [
                            DocumentProblem(line=_src.start.line, column=_src.start.column,
                                            message="{}: {}".format(sink.port_id, e),
                                            problem_type=DocumentProblem.Type.error,
                                            problem_class=DocumentProblem.Class.cwl)]
                        continue

        return connections

    # todo: deprecate this - it's not really needed
    def find_connection(self, conn: Connection) -> ((int, int), None):
        for existing_conn in self.connections:
            if existing_conn == conn:
                return existing_conn.line
        else:
            return None
