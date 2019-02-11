import pathlib

import pytest

from benten.editing.cwldoc import CwlDoc


current_path = pathlib.Path(__file__).parent


def test_basics_salmon():

    wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")
    c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)
    cwl = c.cwl_dict

    assert c.process_type() == "Workflow"

    assert cwl["steps"]["Salmon_Quant___Reads"]["in"]["salmon_index_archive"].start_line == 2093
    assert cwl["steps"]["Salmon_Quant___Reads"]["in"]["salmon_index_archive"]["source"] == "Salmon_Index/salmon_index_archive"


def test_inline_salmon():

    wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")
    c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)

    c2 = c.get_nested_inline_step(("SBG_Create_Expression_Matrix___Transcripts",))
    cwl = c2.cwl_dict

    assert c2.process_type() == "CommandLineTool"

    assert cwl["class"] == "CommandLineTool"
    assert cwl["inputs"]["output_name"].start_line == 634 - 629

    c2 = c.get_nested_inline_step(("Salmon_Quant___Reads",))
    cwl = c2.cwl_dict

    assert cwl["class"] == "CommandLineTool"
    assert cwl["outputs"]["mapping_info"].start_line == 2955 - 2160


def test_nested_inline():

    wf_path = pathlib.Path(current_path, "cwl/002.nested.inline.sbg.eco/wf3.cwl")
    c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)

    c2 = c.get_nested_inline_step(("wf2", "wf1", "wf0", "split"))
    cwl = c2.cwl_dict

    assert cwl["class"] == "CommandLineTool"
    assert cwl["inputs"]["input"].start_line == 1021 - 1013

    c2 = c.get_nested_inline_step(("wf2", "wf1", "wf0"))
    cwl = c2.cwl_dict

    assert cwl["steps"]["pass_through"]["in"]["input"].start_line == 1071 - 987

    with pytest.raises(RuntimeError):
        c3 = c2.get_nested_inline_step(("split",))


def test_nested_inline_both_list_and_dict():
    # Need to make sure we handle both lists and dicts

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-nested-step-as-dict.cwl")
    c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)

    c2 = c.get_nested_inline_step(("s1",))
    cwl = c2.cwl_dict

    assert cwl["class"] == "CommandLineTool"
    assert cwl["inputs"].start_line == 23 - 21

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-nested-step-as-list.cwl")
    c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)

    c2 = c.get_nested_inline_step(("s1",))
    cwl = c2.cwl_dict

    assert cwl["class"] == "CommandLineTool"
    assert cwl["inputs"].start_line == 23 - 21


def test_edits_of_nested_inline():
    wf_path = pathlib.Path(current_path, "cwl/002.nested.inline.sbg.eco/wf3.cwl")
    c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)

    nested_path = ("wf2", "wf1", "wf0", "split")
    c2 = c.get_nested_inline_step(nested_path)

    new_cwl = \
"""class: CommandLineTool
cwlVersion: v1.0
$namespaces:
  sbg: 'https://sevenbridges.com'
id: kghose/benten-demo/split/0
baseCommand:
  - split
inputs:
  - id: input
    type: File?
    inputBinding:
      position: 0
outputs:
  - id: output
    type: 'File[]?'
    outputBinding:
      glob: out-*
label: My new split
arguments:
  - position: 0
    prefix: '-l'
    valueFrom: '1'
  - position: 100
    prefix: ''
    valueFrom: out-
requirements:
  - class: DockerRequirement
    dockerPull: alpine

# I modified this by changing the label and
# removing a bunch of sbg tags at the end and
# added this comment
"""
    new_base_cwl = c.get_raw_cwl_of_base_after_nested_edit(inline_path=nested_path, new_cwl=new_cwl)
    new_c = CwlDoc(raw_cwl=new_base_cwl, path=wf_path, inline_path=None)

    new_c2 = new_c.get_nested_inline_step(nested_path)

    assert new_c2.process_type() == "CommandLineTool"
    assert new_c2.cwl_dict["label"] == "My new split"
    assert new_c2.raw_cwl.endswith("# added this comment")

    with pytest.raises(RuntimeError):
        _ = c2.get_raw_cwl_of_base_after_nested_edit(inline_path=nested_path, new_cwl=new_cwl)
