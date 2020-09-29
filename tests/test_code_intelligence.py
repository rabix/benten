#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from lib import load, load_type_dicts

from benten.langserver.lspobjects import Position, Location


current_path = pathlib.Path(__file__).parent
schema_path = pathlib.Path(current_path, "../benten/000.package.data/")


type_dicts=load_type_dicts()
path = current_path / "cwl" / "ebi" / "workflows" / "cmsearch-multimodel-wf.cwl"


def test_definition():
    doc = load(doc_path=path, type_dicts=type_dicts)
    linked_uri = pathlib.Path(current_path / "cwl" / "ebi" / "utils" / "concatenate.cwl")
    doc_def_loc = doc.definition(loc=Position(50, 20))
    assert isinstance(doc_def_loc, Location)
    assert doc_def_loc.uri == linked_uri.as_uri()


def test_record_field_completion():
    doc = load(doc_path=path, type_dicts=type_dicts)
    cmpl = doc.completion(Position(7, 0))
    assert "doc" in [c.label for c in cmpl]


def test_type_completion():
    doc = load(doc_path=path, type_dicts=type_dicts)
    cmpl = doc.completion(Position(14, 11))
    assert "string" in [c.label for c in cmpl]


def test_step_input_completion():
    doc = load(doc_path=path, type_dicts=type_dicts)
    cmpl = doc.completion(Position(37, 38))
    assert "covariance_models" in [c.label for c in cmpl]


def test_requirement_completion():
    doc = load(doc_path=path, type_dicts=type_dicts)
    cmpl = doc.completion(Position(8, 16))
    assert "InlineJavascriptRequirement" in [c.label for c in cmpl]


def test_requirement_sub_completion():
    this_path = current_path / "cwl" / "ebi" / "workflows" / "InterProScan-v5-chunked-wf.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)
    cmpl = doc.completion(Position(8, 10))
    assert "InlineJavascriptRequirement" in [c.label for c in cmpl]


def test_missing_name_space():
    this_path = current_path / "cwl" / "misc" / "cl-missing-namespace.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)
    assert len(doc.problems) == 1
    namespace_problem = next(p for p in doc.problems if p.range.start.line == 15)
    assert namespace_problem.message.startswith("Expecting one of")


def test_unused_input():
    this_path = current_path / "cwl" / "misc" / "wf-unused-input.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)
    assert len(doc.problems) == 1
    namespace_problem = next(p for p in doc.problems if p.range.start.line == 4)
    assert namespace_problem.message.startswith("Unused input")


def test_implicit_inputs():
    this_path = current_path / "cwl" / "misc" / "wf-when-input.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)
    assert len(doc.problems) == 0

    cmpl = doc.completion(Position(12, 8))
    assert "new_input" in [c.label for c in cmpl]


def test_invalid_input():
    this_path = current_path / "cwl" / "misc" / "wf-invalid-input.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)
    assert len(doc.problems) == 1


def test_port_completer():
    this_path = current_path / "cwl" / "misc" / "wf-port-completer.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)

    cmpl = doc.completion(Position(10, 14))  # Not a list
    assert "in1" in [c.label for c in cmpl]

    cmpl = doc.completion(Position(23, 11))  # Is a list
    assert "out1" in [c.label for c in cmpl]

    cmpl = doc.completion(Position(24, 9))  # Is a list
    assert "in1" in [c.label for c in cmpl]


# This test is somewhat brittle because it assumes the
# existence of this repository on github. If github
# disappears, or this repository is no longer hosted there
# the CWL for this test will have to be updated.
def test_remote_files():
    this_path = current_path / "cwl" / "misc" / "wf-remote-steps.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)

    # Refers to an earlier commit
    hov = doc.hover(Position(13, 32))
    assert "class:" in hov.contents.value

    # Non existent commit
    hov = doc.hover(Position(19, 32))
    assert hov.contents.value == "```\n\n```"


def test_plain_text_include():
    this_path = current_path / "cwl" / "misc" / "cl-include-text.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)

    assert len(doc.problems) == 0

    hov = doc.hover(Position(9, 21))
    assert "We hold" in hov.contents.value
    # Hover should show contents of included file


def test_schemadef_import():
    this_path = current_path / "cwl" / "misc" / "cl-schemadef-import.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)

    assert len(doc.problems) == 0

    cmpl = doc.completion(Position(12, 21))
    assert "cl-schemadef-import.cwl" in [c.label for c in cmpl]
    # The completer should look for all files in the current directory

    cmpl = doc.completion(Position(4, 11))
    assert "./paired_end_record.yml#paired_end_options" in [c.label for c in cmpl]
    # The completer should offer user defined types as completions too


def test_schemadef_include():
    this_path = current_path / "cwl" / "misc" / "cl-schemadef-include.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)

    assert len(doc.problems) == 2

    syntax_error = next(p for p in doc.problems if p.range.start.line == 12)
    assert syntax_error.message == "Expecting an $import"

    type_error = next(p for p in doc.problems if p.range.start.line == 4)
    assert type_error.message.startswith("Expecting one of")


def test_hints_imports():
    this_path = current_path / "cwl" / "misc" / "cl-hints-import.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)

    assert len(doc.problems) == 1

    missing_error = next(p for p in doc.problems if p.range.start.line == 4)
    assert missing_error.message.startswith("Missing document:")

    cmpl = doc.completion(Position(4, 20))
    assert "cl-schemadef-import.cwl" in [c.label for c in cmpl]
    # The completer should look for all files in the current directory


def test_requirements_completion():
    this_path = current_path / "cwl" / "misc" / "cl-hints-dict.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)

    cmpl = doc.completion(Position(12, 8))
    assert "dockerLoad" in [c.label for c in cmpl]

    this_path = current_path / "cwl" / "misc" / "cl-hints-list.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)

    cmpl = doc.completion(Position(12, 8))
    assert "dockerImport" in [c.label for c in cmpl]

    this_path = current_path / "cwl" / "misc" / "cl-hints-dict-start.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)

    cmpl = doc.completion(Position(12, 5))
    assert "dockerLoad" in [c.label for c in cmpl]


def test_docs_on_hover():
    this_path = current_path / "cwl" / "misc" / "wf-when-input.cwl"
    doc = load(doc_path=this_path, type_dicts=type_dicts)

    hov = doc.hover(Position(10, 6))
    assert "Sibling" in hov.contents.value
    assert hov.contents.kind == "markdown"
