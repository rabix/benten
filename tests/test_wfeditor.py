import pytest
import pathlib
import benten.editing.wfeditor as wfeditor


current_path = pathlib.Path(__file__).parent


hand_edited_cwl_with_yaml_errors = """cwlVersion: v1.0
class: Workflow
inputs:
  inp: File
  ex: string

aaaaaa

outputs:
  classout:
    type: File
    outputSource: compile/classfile

steps:
  untar:
    run: tar-param.cwl
    in:
      tarfile: inp
      extractfile: ex
    out: [example_out]

  compile:
    run: arguments.cwl
    in:
      src: untar/example_out
    out: [classfile]"""


hand_edited_cwl_with_cwl_error = """cwlVersion: v1.0
class: Workflow
inputs:
  inp: File
  ex: string

outputs:
  classout:
    type: File
    outputSource: compile/classfile

steps:
  blank_step:
  untar:
    run: tar-param.cwl
    in:
      tarfile: inp
      extractfile: ex
    out: [example_out]

  compile:
    run: arguments.cwl
    in:
      src: untar/example_out
    out: [classfile]"""

# https://bitbucket.org/ruamel/yaml/issues/265/round-trip-adds-new-line-to-end-of-raw


def test_wfeditor_invalid_yaml():
    wf_path = pathlib.Path(current_path, "cwl/001.basic/virtual.cwl").expanduser().resolve().absolute()
    editor = wfeditor.WorkflowEditor(hand_edited_cwl_with_yaml_errors, wf_path)

    assert editor.cwl_doc is None


def test_wfeditor_invalid_cwl():
    wf_path = pathlib.Path(current_path, "cwl/001.basic/virtual.cwl").expanduser().resolve().absolute()
    editor = wfeditor.WorkflowEditor(hand_edited_cwl_with_cwl_error, wf_path)

    assert editor.cwl_doc is not None
    assert len(editor.wf.problems_with_wf) == 1


def test_wfeditor_basics():
    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl").expanduser().resolve().absolute()
    original_yaml = open(wf_path, "r").read()
    editor = wfeditor.WorkflowEditor(original_yaml, wf_path)

    assert len(editor.wf.steps) == 2

    editor.manual_edit(hand_edited_cwl_with_yaml_errors)

    assert editor.cwl_doc is None
    assert editor.as_text() == hand_edited_cwl_with_yaml_errors

    editor.undo()
    assert editor.as_text() == original_yaml

    editor.redo()
    assert editor.as_text() == hand_edited_cwl_with_yaml_errors


basic_wf = """cwlVersion: v1.0
class: Workflow

inputs:
  inp: File
  ex: string

outputs:
  classout:
    type: File
    outputSource: compile/classfile

steps:
  untar:
    run: tar-param.cwl
    in:
      tarfile: inp
      extractfile: ex
    out: [example_out]

  compile:
    run: arguments.cwl
    in:
      src: untar/example_out
    out: [classfile]
"""


def test_wfeditor_add_input():
    wf_path = pathlib.Path(current_path, "cwl/001.basic/virtual.cwl").expanduser().resolve().absolute()
    editor = wfeditor.WorkflowEditor(basic_wf, wf_path)
    editor.add_wf_input("new_input")

    editor.undo()
    assert editor.as_text() == basic_wf

    editor.redo()
    assert "new_input" in editor.cwl_doc["inputs"]


def test_wfeditor_add_output():
    wf_path = pathlib.Path(current_path, "cwl/001.basic/virtual.cwl").expanduser().resolve().absolute()
    editor = wfeditor.WorkflowEditor(basic_wf, wf_path)
    editor.add_wf_output("new_output")

    editor.undo()
    assert editor.as_text() == basic_wf

    editor.redo()
    assert "new_output" in editor.cwl_doc["outputs"]


def test_wfeditor_add_step():
    wf_path = pathlib.Path(current_path, "cwl/001.basic/virtual.cwl").expanduser().resolve().absolute()
    editor = wfeditor.WorkflowEditor(basic_wf, wf_path)
    editor.add_step(run_path=pathlib.Path(current_path, "cwl/001.basic/tar-param.cwl").absolute())

    editor.undo()
    assert editor.as_text() == basic_wf

    editor.redo()
    assert "tar_param" in editor.cwl_doc["steps"]