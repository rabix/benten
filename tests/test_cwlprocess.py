import pathlib
import os
import shutil
import pytest

from benten.editing.cwlprocess import CwlProcess, ViewType, LockedDueToYAMLErrors

current_path = pathlib.Path(__file__).parent


test_dir = "cwlprocess-test-temp-cwl-dir"


def setup():
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)


def teardown():
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_create_from_file():
    path = pathlib.Path(current_path, "cwl", "001.basic", "wf-nested-step-as-list.cwl")
    cwl_process = CwlProcess.create_from_file(path=path)

    assert cwl_process.view_type == ViewType.Process

    ch_p = cwl_process.create_child_view_from_path(("steps", "s1", "run"))
    assert ch_p.view_type == ViewType.Process

    ch_p = cwl_process.create_child_view_from_path(("class",))
    # We wouldn't pick THIS to edit as a view, but the principle works
    assert ch_p.view_type == ViewType.Doc


def test_create_from_file_with_yaml_errors():
    path = pathlib.Path(current_path, "cwl", "000.with.errors", "yaml.errors.cwl")
    cwl_process = CwlProcess.create_from_file(path=path)

    assert cwl_process.view_type == ViewType.Process

    with pytest.raises(LockedDueToYAMLErrors):
        _ = cwl_process.create_child_view_from_path(("steps", "untar", "run"))


# def test_create_from_cursor():
#     path = pathlib.Path(current_path, "cwl", "001.basic", "wf-nested-step-as-list.cwl")
#     cwl_process = CwlProcess.create_from_file(path=path)
#
#     ch_p = cwl_process.create_child_view_from_cursor(line=20, column=10)
#     assert ch_p.view_type == ViewType.Process
#     assert ch_p.parent_view == cwl_process
#     assert ch_p.raw_cwl.startswith("class: CommandLineTool")


def test_add_step_when_empty():
    path = pathlib.Path(current_path, test_dir, "empty-step-dict.cwl")
    with open(path, "w") as f:
        f.write("""class: Workflow
cwlVersion: v1.0
doc: ''
id: test
label: test
inputs: []
outputs: []
steps:
  s1:
    label: step1
    doc:
    in: []
    out: []
    run: {}
    scatter: 
    scatterMethod: 
    hints: []
    requirements: []""")

    cwl_process = CwlProcess.create_from_file(path=path)
    ch_p = cwl_process.create_child_view_from_path(("steps", "s1", "run"))

    new_raw_cwl = """class: CommandLineTool
inputs:
  c: File
  b: string
  e: int
outputs:
  d: string
  f: File
"""

    expected_inserted_text = """
      class: CommandLineTool
      inputs:
        c: File
        b: string
        e: int
      outputs:
        d: string
        f: File
"""

    edit = ch_p.get_edit_from_new_text(new_raw_cwl)

    assert edit.text == expected_inserted_text


def test_edit_step_when_list():
    path = pathlib.Path(current_path, "cwl", "001.basic", "wf-nested-step-as-list.cwl")
    cwl_process = CwlProcess.create_from_file(path=path)

    ch_p = cwl_process.create_child_view_from_path(("steps", "s1", "run"))
    ch_p2 = cwl_process.create_child_view_from_path(("steps", "s1", "run"))

    assert ch_p == ch_p2
    assert ch_p.view_type == ViewType.Process
    assert ch_p.parent_view == cwl_process

    expected_raw_cwl = """class: CommandLineTool
inputs:
  c: File
  b: string
outputs:
  d: string
"""
    assert ch_p.raw_cwl == expected_raw_cwl

    new_raw_cwl = """class: CommandLineTool
inputs:
  c: File
  b: string
  e: int
outputs:
  d: string
  f: File
"""

    expected_inserted_text = """class: CommandLineTool
       inputs:
         c: File
         b: string
         e: int
       outputs:
         d: string
         f: File
"""

    edit = ch_p.get_edit_from_new_text(new_raw_cwl)

    assert edit.text == expected_inserted_text


def test_edit_nested_step():
    path = pathlib.Path(current_path, "cwl", "001.basic", "wf-nested-multiple-levels.cwl")
    cwl_process = CwlProcess.create_from_file(path=path)

    ch_p = cwl_process.create_child_view_from_path(("steps", "s2", "run", "steps", "s1", "run"))
    expected_raw_cwl = """class: CommandLineTool
inputs:
  c: File
outputs:
  d: File
"""
    assert ch_p.raw_cwl == expected_raw_cwl

    new_raw_cwl = """class: CommandLineTool
inputs:
  c: File
  b: string
outputs:
  d: string
  f: File
"""
    expected_inserted_text = """class: CommandLineTool
               inputs:
                 c: File
                 b: string
               outputs:
                 d: string
                 f: File
"""
    edit = ch_p.get_edit_from_new_text(new_raw_cwl)

    assert edit.text == expected_inserted_text


def test_edit_propagation_nested_step():
    path = pathlib.Path(current_path, "cwl", "001.basic", "wf-nested-multiple-levels.cwl")
    parent = CwlProcess.create_from_file(path=path)

    ch1 = parent.create_child_view_from_path(("steps", "s2", "run"))
    ch2 = parent.create_child_view_from_path(("steps", "s2", "run", "steps", "s1", "run"))

    new_raw_cwl = """class: CommandLineTool
inputs:
  c: File
  b: string
outputs:
  d: string
  f: File
"""

    expected_parent_text = """
class: Workflow
inputs:
  a: File
  b: string
outputs:
  a:
    outputSource: [s1/d, s2/d]
steps:

  s1:
    in:
       c: a
    out:
       d: File
    run:
       class: CommandLineTool
       inputs:
         c: File
       outputs:
         d: File

  s2:
    in:
       b: b
    out:
       d: File
    run:
        class: Workflow
        inputs:
          a: File
        outputs:
          a:
            outputSource: s1/d
        steps:

          s1:
            in:
               c: a
            out:
               d: File
            run:
               class: CommandLineTool
               inputs:
                 c: File
                 b: string
               outputs:
                 d: string
                 f: File
"""
    ch2.apply_raw_text(new_raw_cwl)
    assert parent.raw_cwl == expected_parent_text

    expected_ch1_text = """class: Workflow
inputs:
  a: File
outputs:
  a:
    outputSource: s1/d
steps:

  s1:
    in:
       c: a
    out:
       d: File
    run:
       class: CommandLineTool
       inputs:
         c: File
         b: string
       outputs:
         d: string
         f: File
"""
    assert ch1.raw_cwl == expected_ch1_text

    expected_ch2_text = """class: CommandLineTool
inputs:
  c: File
  b: string
outputs:
  d: string
  f: File
"""
    assert ch2.raw_cwl == expected_ch2_text


def test_edit_propagation_nested_step2():
    path = pathlib.Path(current_path, "cwl", "001.basic", "wf-nested-multiple-levels.cwl")
    parent = CwlProcess.create_from_file(path=path)

    ch1 = parent.create_child_view_from_path(("steps", "s1", "run"))

    new_raw_cwl = """class: CommandLineTool
inputs:
  c: File
  b: string
outputs:
  d: string
  f: File

"""

    expected_parent_text = """
class: Workflow
inputs:
  a: File
  b: string
outputs:
  a:
    outputSource: [s1/d, s2/d]
steps:

  s1:
    in:
       c: a
    out:
       d: File
    run:
       class: CommandLineTool
       inputs:
         c: File
         b: string
       outputs:
         d: string
         f: File

  s2:
    in:
       b: b
    out:
       d: File
    run:
        class: Workflow
        inputs:
          a: File
        outputs:
          a:
            outputSource: s1/d
        steps:

          s1:
            in:
               c: a
            out:
               d: File
            run:
               class: CommandLineTool
               inputs:
                 c: File
               outputs:
                 d: File
"""
    ch1.apply_raw_text(new_raw_cwl)
    assert parent.raw_cwl == expected_parent_text

    expected_ch1_text = """class: CommandLineTool
inputs:
  c: File
  b: string
outputs:
  d: string
  f: File

"""
    assert ch1.raw_cwl == expected_ch1_text


def test_view_deleted_from_parent():
    pass


def test_expression_changed_to_scalar_type_in_parent():
    pass


def test_child_view_of_step_with_empty_dict():
    pass

#
# def test_malformed():
#
#     raw_cwl = "id: ["
#     c = CwlDoc(raw_cwl=raw_cwl, path=pathlib.Path("empty.cwl"), inline_path=None)
#     c.compute_cwl_dict()
#     assert len(c.yaml_error) == 1
#     assert c.yaml_error[0].line == 1
#     assert c.yaml_error[0].column == 0
#
#     c = CwlDoc(raw_cwl="id: [", path=pathlib.Path("empty.cwl"), inline_path=None,
#                yaml_error=DocumentError(0, 0, "Make sure this error is preserved"))
#     c.compute_cwl_dict()
#     assert len(c.yaml_error) == 2
#     assert c.yaml_error[0].line == 0
#     assert c.yaml_error[0].column == 0
#
#
# # The salmon workflow is a real workflow developed on the SBG platform. It has the benefit of
# # having nested workflows, blank lines, comments etc.
#
# def test_round_trip_salmon():
#
#     wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")
#     raw_cwl = wf_path.open("r").read()
#     c = CwlDoc(raw_cwl=raw_cwl, path=wf_path, inline_path=None)
#     assert raw_cwl == "".join(c.cwl_lines)
#     assert c.cwl_dict is None
#
#
# def test_basics_salmon():
#
#     wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")
#     c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)
#
#     c.compute_cwl_dict()
#     cwl = c.cwl_dict
#
#     assert c.process_type() == "Workflow"
#
#     assert cwl["steps"]["Salmon_Quant___Reads"]["in"]["salmon_index_archive"].start.line == 2093
#     assert cwl["steps"]["Salmon_Quant___Reads"]["in"]["salmon_index_archive"]["source"] == \
#            "Salmon_Index/salmon_index_archive"
#
#
# def test_inline_salmon():
#
#     wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")
#     c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)
#
#     c.compute_cwl_dict()
#     c2 = c.get_nested_inline_step(("SBG_Create_Expression_Matrix___Transcripts",))
#     c2.compute_cwl_dict()
#     cwl = c2.cwl_dict
#
#     assert c2.process_type() == "CommandLineTool"
#
#     assert cwl["class"] == "CommandLineTool"
#     assert cwl["inputs"]["output_name"].start.line == 634 - 629
#
#     c2 = c.get_nested_inline_step(("Salmon_Quant___Reads",))
#     c2.compute_cwl_dict()
#     cwl = c2.cwl_dict
#
#     assert cwl["class"] == "CommandLineTool"
#     assert cwl["outputs"]["mapping_info"].start.line == 2955 - 2160
#
#
# def test_nested_inline():
#
#     wf_path = pathlib.Path(current_path, "cwl/002.nested.inline.sbg.eco/wf3.cwl")
#     c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)
#
#     c.compute_cwl_dict()
#     c2 = c.get_nested_inline_step(("wf2", "wf1", "wf0", "split"))
#     c2.compute_cwl_dict()
#     cwl = c2.cwl_dict
#
#     assert cwl["class"] == "CommandLineTool"
#     assert cwl["inputs"]["input"].start.line == 1021 - 1013
#
#     c2 = c.get_nested_inline_step(("wf2", "wf1", "wf0"))
#     c2.compute_cwl_dict()
#     cwl = c2.cwl_dict
#
#     assert cwl["steps"]["pass_through"]["in"]["input"].start.line == 1071 - 987
#
#     with pytest.raises(RuntimeError):
#         c3 = c2.get_nested_inline_step(("split",))
#
#
# def test_nested_inline_both_list_and_dict():
#     # Need to make sure we handle both lists and dicts
#
#     wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-nested-step-as-dict.cwl")
#     c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)
#
#     c.compute_cwl_dict()
#     c2 = c.get_nested_inline_step(("s1",))
#     c2.compute_cwl_dict()
#     cwl = c2.cwl_dict
#
#     assert cwl["class"] == "CommandLineTool"
#     assert cwl["inputs"].start.line == 23 - 21
#
#     wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-nested-step-as-list.cwl")
#     c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)
#
#     c.compute_cwl_dict()
#     c2 = c.get_nested_inline_step(("s1",))
#     c2.compute_cwl_dict()
#     cwl = c2.cwl_dict
#
#     assert cwl["class"] == "CommandLineTool"
#     assert cwl["inputs"].start.line == 23 - 21
#
#
# def test_edits_of_nested_inline_null():
#     wf_path = pathlib.Path(current_path, "cwl/002.nested.inline.sbg.eco/wf3.cwl")
#     c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)
#
#     nested_path = ("wf2", "wf1", "wf0", "split")
#     c.compute_cwl_dict()
#     c2 = c.get_nested_inline_step(nested_path)
#
#     new_cwl = c2.raw_cwl
#
#     new_base_cwl = c.get_raw_cwl_of_base_after_nested_edit(inline_path=nested_path, new_cwl=new_cwl)
#     new_c = CwlDoc(raw_cwl=new_base_cwl, path=wf_path, inline_path=None)
#
#     assert new_c.raw_cwl == c.raw_cwl
#
#
# def test_edits_of_nested_inline():
#     wf_path = pathlib.Path(current_path, "cwl/002.nested.inline.sbg.eco/wf3.cwl")
#     c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)
#
#     nested_path = ("wf2", "wf1", "wf0", "split")
#     c.compute_cwl_dict()
#     c2 = c.get_nested_inline_step(nested_path)
#
#     new_cwl = \
# """class: CommandLineTool
# cwlVersion: v1.0
# $namespaces:
#   sbg: 'https://sevenbridges.com'
# id: kghose/benten-demo/split/0
# baseCommand:
#   - split
# inputs:
#   - id: input
#     type: File?
#     inputBinding:
#       position: 0
# outputs:
#   - id: output
#     type: 'File[]?'
#     outputBinding:
#       glob: out-*
# label: My new split
# arguments:
#   - position: 0
#     prefix: '-l'
#     valueFrom: '1'
#   - position: 100
#     prefix: ''
#     valueFrom: out-
# requirements:
#   - class: DockerRequirement
#     dockerPull: alpine
#
# # I modified this by changing the label and
# # removing a bunch of sbg tags at the end and
# # added this comment
# """
#     new_base_cwl = c.get_raw_cwl_of_base_after_nested_edit(inline_path=nested_path, new_cwl=new_cwl)
#     new_c = CwlDoc(raw_cwl=new_base_cwl, path=wf_path, inline_path=None)
#     new_c.compute_cwl_dict()
#     new_c2 = new_c.get_nested_inline_step(nested_path)
#     new_c2.compute_cwl_dict()
#
#     assert new_c2.process_type() == "CommandLineTool"
#     assert new_c2.cwl_dict["label"] == "My new split"
#     assert new_c2.raw_cwl.endswith("# added this comment\n")
#
#     with pytest.raises(RuntimeError):
#         _ = c2.get_raw_cwl_of_base_after_nested_edit(inline_path=nested_path, new_cwl=new_cwl)
