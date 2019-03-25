import pathlib
import os
import shutil
import pytest

from benten.editing.rootyamlview import RootYamlView
import benten.models.workflow as WF

current_path = pathlib.Path(__file__).parent


test_dir = "workflowedit-test-dir"


def setup():
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)


def teardown():
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def create_cwl(cwl, fname):
    path = pathlib.Path(test_dir, fname)
    with open(path, "w") as f:
        f.write(cwl)
    return path


def test_add_to_doc_missing_step_field():
    wf_with_no_step = """class: Workflow"""
    wf_path = pathlib.Path(test_dir, "no-step.cwl")
    cwl_doc = RootYamlView(raw_text=wf_with_no_step,
                           file_path=wf_path)
    wf = WF.Workflow(cwl_doc=cwl_doc)

    edit = wf.add_step(pathlib.Path(current_path, "cwl/001.basic/arguments.cwl"))

    assert edit.start.line == 1
    assert edit.start.column == 0
    assert edit.end is None

    lines = edit.text.splitlines()
    assert lines[1].lstrip().startswith("arguments.cwl:")
    assert len(lines[1]) - len(lines[1].lstrip()) == 2


def test_add_to_doc_empty_step_field():
    wf_with_empty_step = """class: Workflow\nsteps: []"""
    wf_path = pathlib.Path(test_dir, "empty-step.cwl")
    cwl_doc = RootYamlView(raw_text=wf_with_empty_step,
                           file_path=wf_path)
    wf = WF.Workflow(cwl_doc=cwl_doc)

    edit = wf.add_step(pathlib.Path(current_path, "cwl/001.basic/arguments.cwl"))

    assert edit.start.line == 1
    assert edit.start.column == 0
    assert edit.end.line == 1
    assert edit.end.column == 9

    lines = edit.text.splitlines()
    assert lines[1].lstrip().startswith("arguments.cwl:")
    assert len(lines[1]) - len(lines[1].lstrip()) == 2


def test_add_local_step_list():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-list.cwl").resolve()
    cwl_doc = RootYamlView(raw_text=wf_path.open("r").read(),
                           file_path=wf_path)
    wf = WF.Workflow(cwl_doc=cwl_doc)

    edit = wf.add_step(pathlib.Path(current_path, "cwl/001.basic/arguments.cwl"))

    assert edit.start.line == 24
    assert edit.start.column == 0
    assert edit.end is None

    lines = edit.text.splitlines()
    assert len(lines[0]) - len(lines[0].lstrip()) == 2
    assert lines[0].lstrip().startswith("- id:")


def test_add_local_step_dict():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl").resolve()
    cwl_doc = RootYamlView(raw_text=wf_path.open("r").read(),
                           file_path=wf_path)
    wf = WF.Workflow(cwl_doc=cwl_doc)

    edit = wf.add_step(pathlib.Path(current_path, "cwl/001.basic/arguments.cwl"))

    assert edit.start.line == 24
    assert edit.start.column == 0
    assert edit.end is None

    lines = edit.text.splitlines()
    assert len(lines[0]) - len(lines[0].lstrip()) == 2
    assert lines[0].lstrip().startswith("arguments.cwl:")


def test_add_local_step_with_id():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl").resolve()
    cwl_doc = RootYamlView(raw_text=wf_path.open("r").read(),
                           file_path=wf_path)
    wf = WF.Workflow(cwl_doc=cwl_doc)

    edit = wf.add_step(pathlib.Path(current_path, "cwl/001.basic/withid.cwl"))

    lines = edit.text.splitlines()
    assert len(lines[0]) - len(lines[0].lstrip()) == 2
    assert lines[0].lstrip().startswith("like_a_rock:")


def test_add_duplicate_step():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl").resolve()
    cwl_doc = RootYamlView(raw_text=wf_path.open("r").read(),
                           file_path=wf_path)
    wf = WF.Workflow(cwl_doc=cwl_doc)
    edit = wf.add_step(pathlib.Path(current_path, "cwl/001.basic/withid.cwl"))
    cwl_doc._apply_edit_to_lines(edit)

    wf = WF.Workflow(cwl_doc=cwl_doc)
    edit = wf.add_step(pathlib.Path(current_path, "cwl/001.basic/withid.cwl"))

    lines = edit.text.splitlines()
    assert lines[0].lstrip().startswith("like_a_rock_1:")
    assert lines[3].lstrip() == "in: []"


def test_indentation():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-list-indent4.cwl").resolve()
    cwl_doc = CwlProcess.create_from_file(wf_path)
    cwl_doc.compute_cwl_dict()
    wf = WF.Workflow(cwl_doc=cwl_doc)
    edit = wf.add_step(pathlib.Path(current_path, "cwl/001.basic/withid.cwl"))

    lines = edit.text.splitlines()
    assert len(lines[0]) - len(lines[0].lstrip()) == 4
