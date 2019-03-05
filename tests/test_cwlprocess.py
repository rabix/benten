import pathlib

import pytest

from benten.editing.cwlprocess import CwlProcess, ViewType, LockedDueToYAMLErrors, DocumentError
from benten.editing.edit import Edit

current_path = pathlib.Path(__file__).parent


def editor_simulator(existing_text: str, edit: Edit):
    # from PySide2.QtGui import QTextDocument, QTextCursor
    #
    # doc = QTextDocument(existing_text)
    # cursor = QTextCursor(doc)
    # cursor.clearSelection()
    #
    # if edit.start.line == doc.blockCount():
    #     if edit.start.column != 0:
    #         raise RuntimeError("Implementation error! File bug report with stack trace please")
    #     cursor.movePosition(cursor.End)
    #     cursor.insertText("\n")
    # else:
    #     cursor.movePosition(cursor.Start)
    #     cursor.movePosition(cursor.NextBlock, n=edit.start.line)  # blocks == lines
    #     cursor.movePosition(cursor.Right, n=edit.start.column)
    #
    # if edit.end is not None:
    #     delta_line = edit.end.line - edit.start.line
    #     delta_col = edit.end.column - edit.start.column
    #     if delta_line > 0:
    #         cursor.movePosition(cursor.NextBlock, cursor.KeepAnchor, n=delta_line)
    #     else:
    #         cursor.movePosition(cursor.Right, cursor.KeepAnchor, n=delta_col)
    #
    # cursor.insertText(edit.text)
    #
    # return doc.toPlainText()

    existing_lines = existing_text.splitlines(keepends=True)
    lines_to_insert = edit.text.splitlines(keepends=True)

    if edit.end is None:
        edit.end = edit.start

    new_lines = existing_lines[:edit.start.line] + \
                [existing_lines[edit.start.line][:edit.start.column]] + \
                lines_to_insert + \
                (([existing_lines[edit.end.line][edit.end.column:]] +
                (existing_lines[edit.end.line + 1:] if edit.end.line + 1 < len(existing_lines) else []))
                 if edit.end.line < len(existing_lines) else [])

    return "".join(new_lines)


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
    edit = ch2.get_edit_from_new_text(new_raw_cwl)
    parent.set_raw_cwl(editor_simulator(parent.raw_cwl, edit))
    assert parent.raw_cwl == expected_parent_text

    parent.propagate_edits()

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


def test_edit_chained_nested_step():
    pass


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


# test_edit_propagation_nested_step()