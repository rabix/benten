import copy

from ruamel.yaml.comments import CommentedMap

from benten.models.workflow import Workflow, Connection
import benten.lib as blib


class ConnectionAlreadyPresent(Exception):
    pass


class StepNotFound(Exception):
    pass


# Elementary actions operate on the CommentedMap and return a CommentedMap. This is so that
# We can chain actions when we need to.

_step_template = \
"""label: {step_id}
in: []
out: []
run: {run_path}
"""


def _add_step(cwl_doc: CommentedMap, rel_run_path: str, step_id: str) -> CommentedMap:
    """Add step to end of all the steps"""

    new_step = blib.yamlify(_step_template.format(step_id=step_id, run_path=rel_run_path))

    new_wf_doc = copy.deepcopy(cwl_doc)
    blib.lom(new_wf_doc["steps"]).append(step_id, new_step)

    return new_wf_doc


_wf_input_template = \
"""type:
default:
label:
format:
doc:
"""


def _add_wf_input(cwl_doc: CommentedMap, input_id: str) -> CommentedMap:
    new_wf_doc = copy.deepcopy(cwl_doc)
    blib.lom(new_wf_doc["inputs"]).append(input_id, blib.yamlify(_wf_input_template))
    return new_wf_doc


_wf_output_template = \
"""outputSource: []"""


def _add_wf_output(cwl_doc: CommentedMap, output_id: str) -> CommentedMap:
    new_wf_doc = copy.deepcopy(cwl_doc)
    blib.lom(new_wf_doc["outputs"]).append(output_id, blib.yamlify(_wf_output_template))
    return new_wf_doc


def _add_conn_to_wf_output(cwl_doc: CommentedMap, conn: Connection) -> CommentedMap:
    new_wf_doc = copy.deepcopy(cwl_doc)
    outs = blib.lom(new_wf_doc["outputs"])

    try:
        out_port = outs.get(conn.dst.port_id)
        if "outputSource" in out_port:
            out_port["outputSource"] = blib.smart_append(out_port["outputSource"], str(conn.src))
        else:
            out_port["outputSource"] = str(conn.src)
    except KeyError:
        outs.append(conn.dst.port_id, blib.yamlify("outputSource: {}".format(conn.src)))

    return new_wf_doc


def _add_conn_to_step(cwl_doc: CommentedMap, conn: Connection) -> CommentedMap:
    # We assume that step and port validations have been done prior
    new_wf_doc = copy.deepcopy(cwl_doc)

    step_inputs = blib.lom(blib.lom(new_wf_doc["steps"]).get(conn.dst.node_id)["in"])
    if conn.dst.port_id not in step_inputs:
        step_inputs.append(conn.dst.port_id, blib.yamlify("source: {}".format(conn.src)))
    else:
        step_inputs.get(conn.dst.port_id)["source"] = \
            blib.smart_append(step_inputs.get(conn.dst.port_id)["source"], str(conn.src))

    return new_wf_doc


def _add_connection(cwl_doc: CommentedMap, conn: Connection) -> CommentedMap:
    """We need to add the step/workflow output if it does not exist, then investigate if the
    source/outputSource """
    if conn.dst.node_id is None:
        return _add_conn_to_wf_output(cwl_doc, conn)
    else:
        return _add_conn_to_step(cwl_doc, conn)


def add_connection(workflow: Workflow, conn: Connection) -> CommentedMap:
    if workflow.find_connection(conn) is not None:
        raise ConnectionAlreadyPresent
    return _add_connection(workflow.cwl_doc, conn)