import pytest
import pathlib
import os

import benten.lib as blib
import benten.logic.workflow as WF
import benten.logic.actions as actions

current_path = pathlib.Path(__file__).parent


def test_insert_step_list():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-list.cwl")
    cwl_doc = blib.load_cwl(str(wf_path))

    # wf = WF.Workflow(cwl_doc, wf_fname)
    original_step_count = len(cwl_doc["steps"])

    _run_path = pathlib.Path(current_path, "cwl/small/lib/tools/merge.cwl")
    run_path = os.path.relpath(_run_path, wf_path.parent)

    _new_cwl_doc = actions._add_step(cwl_doc, run_path, "new_step")
    new_cwl_doc = blib.reyamlify(_new_cwl_doc)

    assert len(cwl_doc["steps"]) == original_step_count  # Make sure we don't mutate the original WF
    assert len(new_cwl_doc["steps"]) == original_step_count + 1

    assert "new_step" in blib.lom(new_cwl_doc["steps"])
    assert blib.lom(new_cwl_doc["steps"])["new_step"].lc.line == 24


def test_insert_step_dict():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl")
    cwl_doc = blib.load_cwl(str(wf_path))

    # wf = WF.Workflow(cwl_doc, wf_fname)
    original_step_count = len(cwl_doc["steps"])

    _run_path = pathlib.Path(current_path, "cwl/small/lib/tools/merge.cwl")
    run_path = os.path.relpath(_run_path, wf_path.parent)

    _new_cwl_doc = actions._add_step(cwl_doc, run_path, "new_step")
    new_cwl_doc = blib.reyamlify(_new_cwl_doc)

    assert len(cwl_doc["steps"]) == original_step_count  # Make sure we don't mutate the original WF
    assert len(new_cwl_doc["steps"]) == original_step_count + 1

    assert "new_step" in blib.lom(new_cwl_doc["steps"])
    assert blib.lom(new_cwl_doc["steps"])["new_step"].lc.line == 25


def test_add_wf_input():

    wf_fname = pathlib.Path(current_path, "cwl/small/inner-wf.cwl").resolve()
    cwl_doc = blib.load_cwl(str(wf_fname))

    new_cwl_doc = actions._add_wf_input(cwl_doc, "new_input")
    assert "new_input" in blib.lom(new_cwl_doc["inputs"])

    new_wf = WF.Workflow(blib.reyamlify(new_cwl_doc), wf_fname)
    assert new_wf.inputs["new_input"].line == 11


def test_add_wf_output():

    wf_fname = pathlib.Path(current_path, "cwl/small/inner-wf.cwl").resolve()
    cwl_doc = blib.load_cwl(str(wf_fname))

    new_cwl_doc = actions._add_wf_output(cwl_doc, "new_output")
    assert "new_output" in blib.lom(new_cwl_doc["outputs"])

    new_wf = WF.Workflow(blib.reyamlify(new_cwl_doc), wf_fname)
    assert new_wf.outputs["new_output"].line == 18


def test_add_existing_connection():

    wf_fname = pathlib.Path(current_path, "cwl/small/inner-wf.cwl").resolve()
    cwl_doc = blib.load_cwl(str(wf_fname))
    wf = WF.Workflow(cwl_doc, wf_fname)

    conn = WF.Connection(src=WF.Port(node_id=None, port_id="inner_in"),
                         dst=WF.Port(node_id="split", port_id="split_in"),
                         line=None)
    with pytest.raises(actions.ConnectionAlreadyPresent):
        actions.add_connection(wf, conn)


def test_add_new_input_connection():

    wf_fname = pathlib.Path(current_path, "cwl/small/inner-wf.cwl").resolve()
    cwl_doc = blib.load_cwl(str(wf_fname))

    new_cwl_doc = actions._add_wf_input(cwl_doc, "inner_new_in")

    conn = WF.Connection(src=WF.Port(node_id=None, port_id="inner_new_in"),
                         dst=WF.Port(node_id="pass_through", port_id="pt_in2"),
                         line=None)

    new_cwl_doc = actions._add_connection(new_cwl_doc, conn)

    new_wf = WF.Workflow(blib.reyamlify(new_cwl_doc), wf_fname)

    assert new_wf.find_connection(conn) == 40


def test_add_new_pass_through_connection():

    wf_fname = pathlib.Path(current_path, "cwl/small/inner-wf.cwl").resolve()
    cwl_doc = blib.load_cwl(str(wf_fname))

    new_cwl_doc = actions._add_wf_output(cwl_doc, "inner_new_out")

    conn = WF.Connection(src=WF.Port(node_id=None, port_id="inner_in"),
                         dst=WF.Port(node_id=None, port_id="inner_new_out"),
                         line=None)

    new_cwl_doc = actions._add_connection(new_cwl_doc, conn)
    new_wf = WF.Workflow(blib.reyamlify(new_cwl_doc), wf_fname)

    assert new_wf.find_connection(conn) == 20


def test_append_new_connection():

    wf_fname = pathlib.Path(current_path, "cwl/small/inner-wf.cwl").resolve()
    cwl_doc = blib.load_cwl(str(wf_fname))
    wf = WF.Workflow(cwl_doc, wf_fname)

    conn = WF.Connection(src=WF.Port(node_id=None, port_id="inner_in"),
                         dst=WF.Port(node_id="pass_through", port_id="pt_in1"),
                         line=None)

    new_cwl_doc = actions._add_connection(cwl_doc, conn)
    new_wf = WF.Workflow(blib.reyamlify(new_cwl_doc), wf_fname)

    assert new_wf.find_connection(conn) == 34