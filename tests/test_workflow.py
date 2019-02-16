import pathlib
import pytest

import benten.models.workflow as WF

current_path = pathlib.Path(__file__).parent


def test_parsing_empty_workflow():
    empty_wf = ""
    cwl_doc = WF.CwlDoc(raw_cwl=empty_wf, path=pathlib.Path("./nothing.cwl"))

    with pytest.raises(TypeError):
        _ = WF.Workflow(cwl_doc=cwl_doc)

    cwl_doc.compute_cwl_dict()
    wf = WF.Workflow(cwl_doc=cwl_doc)

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

    cwl_doc = WF.CwlDoc(raw_cwl=wf_with_empty_step, path=pathlib.Path(current_path, "./nothing.cwl").resolve())
    cwl_doc.compute_cwl_dict()
    wf = WF.Workflow(cwl_doc=cwl_doc)
    # Basically we shouldn't choke because there is nothing in that step

    assert len(wf.inputs) == 0
    assert len(wf.steps) == 2
    assert wf.steps["like_a_fish"].process_type == "Workflow"
    assert wf.steps["empty"].process_type == "invalid"

    print(wf.problems_with_wf)


def test_parsing_ports_with_plain_source():
    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-list.cwl").resolve()
    cwl_doc = WF.CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path)
    cwl_doc.compute_cwl_dict()
    wf = WF.Workflow(cwl_doc=cwl_doc)

    conn = next(c for c in wf.connections if c.dst == WF.Port("compile", "src"))
    assert conn.src == WF.Port("untar", "example_out")


def test_interface_parsing():
    """Load CWL and check we interpret the interface correctly"""

    # This is a public SBG workflow
    wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl").resolve()
    cwl_doc = WF.CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path)
    cwl_doc.compute_cwl_dict()
    wf = WF.Workflow(cwl_doc=cwl_doc)

    assert wf.inputs["reads"].line == (21, 31)

    assert wf.outputs["quant_sf"].line == (518, 529)

    assert len(wf.steps) == 5

    assert wf.steps["SBG_Create_Expression_Matrix___Genes"].line == (951, 1284)
    assert len(wf.steps["SBG_Create_Expression_Matrix___Genes"].available_sinks) == 3
    assert len(wf.steps["SBG_Create_Expression_Matrix___Genes"].available_sources) == 1

    assert wf.steps["Salmon_Quant___Reads"].line == (2057, 3514)
    assert wf.steps["Salmon_Quant___Reads"].process_type == "CommandLineTool"

    assert len(wf.steps["Salmon_Index"].available_sinks) == 8
    assert len(wf.steps["Salmon_Index"].available_sources) == 1

def test_connection_parsing():
    """Load CWL and check we interpret the connections correctly"""

    # This workflow contains nested elements at various directory levels. We should handle them
    # correctly. This workflow also has a small number of components so we can count things by
    # hand to put in the tests
    wf_path = pathlib.Path(current_path, "cwl/003.diff.dir.levels/lib/workflows/outer-wf.cwl").resolve()
    cwl_doc = WF.CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path)
    cwl_doc.compute_cwl_dict()
    wf = WF.Workflow(cwl_doc=cwl_doc)

    assert wf.inputs["wf_in2"].line == (11, 15)

    assert wf.outputs["wf_out"].line == (16, 27)

    assert len(wf.steps) == 4

    assert wf.steps["pass_through"].line == (34, 44)
    assert len(wf.steps["pass_through"].available_sinks) == 2
    assert len(wf.steps["pass_through"].available_sources) == 1

    assert len(wf.steps["inner_wf"].available_sinks) == 1
    assert len(wf.steps["inner_wf_1"].available_sources) == 1

    assert len(wf.connections) == 9

    assert len(
        [True for conn in wf.connections
         if conn.dst.node_id == "merge" and conn.dst.port_id == "merge_in"]) == 3

    line = (46, 51)
    assert [conn.line
            for conn in wf.connections
            if conn.dst.node_id == "merge" and conn.dst.port_id == "merge_in"] == [line] * 3

    line = (16, 27)
    assert [conn.line
            for conn in wf.connections
            if conn.dst.port_id == "wf_out"] == [line] * 2


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


# note that find_connection may be deprecated as it has no use
def test_connection_search():
    """Check connection finding"""
    wf_path = pathlib.Path(current_path, "cwl/003.diff.dir.levels/lib/workflows/outer-wf.cwl").resolve()
    cwl_doc = WF.CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path)
    cwl_doc.compute_cwl_dict()
    wf = WF.Workflow(cwl_doc=cwl_doc)

    c1 = WF.Connection(WF.Port(node_id=None, port_id="wf_in2"),
                         WF.Port(node_id=None, port_id="wf_out2"), line=None)
    assert wf.find_connection(c1) == (27, 33)

    c2 = WF.Connection(src=WF.Port(node_id=None, port_id="wf_in"),
                       dst=WF.Port(node_id="pass_through", port_id="pt_in1"),
                       line=None)

    assert wf.find_connection(c2) == (36, 38)

    c3 = WF.Connection(src=WF.Port(node_id=None, port_id="wf_in"),
                       dst=WF.Port(node_id="pass_through", port_id="pt_in2"),
                       line=None)

    assert wf.find_connection(c3) is None
