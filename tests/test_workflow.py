import pathlib

import benten.lib as blib
import benten.logic.workflow as WF

current_path = pathlib.Path(__file__).parent


def test_parsing_of_empty_workflow():
    empty_wf = ""
    wf = WF.Workflow(blib.yamlify(empty_wf), path=pathlib.Path("./nothing.cwl"))

    assert len(wf.inputs) == 0
    assert len(wf.outputs) == 0
    assert len(wf.steps) == 0


def test_parsing_empty_step():
    wf_with_empty_step = """
class: Workflow
cwlVersion: v1.0
inputs: []
outputs: []
steps:
- id: like_a_fish
  label: Umberto Eco
  in: []
  out: []
  run: cwl/sbg/salmon.cwl
- id: empty
"""
    wf = WF.Workflow(blib.yamlify(wf_with_empty_step), path=pathlib.Path(current_path, "nothing.cwl").resolve())


def test_interface_parsing():
    """Load CWL and check we interpret the interface correctly"""

    # This is a public SBG workflow
    fname = pathlib.Path(current_path, "cwl/sbg/salmon.cwl").resolve()
    cwl_doc = blib.load_cwl(str(fname))

    wf = WF.Workflow(cwl_doc, fname)

    #assert wf.inputs.line == 6
    assert wf.inputs["reads"].line == 21

    #assert wf.outputs.line == 504
    assert wf.outputs["quant_sf"].line == 518

    assert len(wf.steps) == 5

    assert wf.steps["SBG_Create_Expression_Matrix___Genes"].line == 951
    assert len(wf.steps["SBG_Create_Expression_Matrix___Genes"].available_sinks) == 3
    assert len(wf.steps["SBG_Create_Expression_Matrix___Genes"].available_sources) == 1

    assert wf.steps["Salmon_Quant___Reads"].line == 2057

    assert len(wf.steps["Salmon_Index"].available_sinks) == 8
    assert len(wf.steps["Salmon_Index"].available_sources) == 1


def test_connection_parsing():
    """Load CWL and check we interpret the connections correctly"""

    # This workflow contains nested elements at various directory levels. We should handle them
    # correctly. This workflow also has a small number of components so we can count things by
    # hand to put in the tests
    fname = pathlib.Path(current_path, "cwl/small/lib/workflows/outer-wf.cwl").resolve()
    cwl_doc = blib.load_cwl(str(fname))

    wf = WF.Workflow(cwl_doc, fname)

    #assert wf.inputs.line == 6
    assert wf.inputs["wf_in2"].line == 11

    #assert wf.outputs.line == 15
    assert wf.outputs["wf_out"].line == 16

    assert len(wf.steps) == 4

    assert wf.steps["pass_through"].line == 34
    assert len(wf.steps["pass_through"].available_sinks) == 2
    assert len(wf.steps["pass_through"].available_sources) == 1

    assert len(wf.steps["inner_wf"].available_sinks) == 1
    assert len(wf.steps["inner_wf_1"].available_sources) == 1

    assert len(wf.connections) == 9

    assert len(
        [True for conn in wf.connections
         if conn.dst.node_id == "merge" and conn.dst.port_id == "merge_in"]) == 3

    assert [conn.line
            for conn in wf.connections
            if conn.dst.node_id == "merge" and conn.dst.port_id == "merge_in"] == [48, 49, 50]

    assert [conn.line
            for conn in wf.connections
            if conn.dst.port_id == "wf_out"] == [18, 19]

    conn = WF.Connection(WF.Port(node_id=None, port_id="wf_in2"),
                         WF.Port(node_id=None, port_id="wf_out2"), line=None)
    assert wf.find_connection(conn) == 29


def test_connection_equivalence():
    """Check for connection equivalence"""

    c1 = WF.Connection(src=WF.Port(node_id=None, port_id="wf_in1"),
                       dst=WF.Port(node_id="step1", port_id="step1_in1"),
                       line=None)
    c2 = WF.Connection(src=WF.Port(node_id=None, port_id="wf_in1"),
                       dst=WF.Port(node_id="step1", port_id="step1_in1"),
                       line=None)

    assert c1 == c2

    c3 = WF.Connection(src=WF.Port(node_id=None, port_id="wf_in1"),
                       dst=WF.Port(node_id="step1", port_id="step1_in2"),
                       line=None)

    assert c1 != c3


def test_connection_search():
    """Check connection finding"""
    fname = pathlib.Path(current_path, "cwl/small/lib/workflows/outer-wf.cwl").resolve()
    cwl_doc = blib.load_cwl(str(fname))

    wf = WF.Workflow(cwl_doc, fname)
    c1 = WF.Connection(src=WF.Port(node_id=None, port_id="wf_in"),
                       dst=WF.Port(node_id="pass_through", port_id="pt_in1"),
                       line=None)

    assert wf.find_connection(c1) == 37

    c2 = WF.Connection(src=WF.Port(node_id=None, port_id="wf_in"),
                       dst=WF.Port(node_id="pass_through", port_id="pt_in2"),
                       line=None)

    assert wf.find_connection(c2) is None
