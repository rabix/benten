import pathlib
import pytest

from benten.editing.lineloader import parse_cwl_with_line_info


current_path = pathlib.Path(__file__).parent


def test_line_number_dict():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl")
    c = parse_cwl_with_line_info(raw_cwl=wf_path.open("r").read())

    assert c["cwlVersion"] == "v1.0"
    assert c.start_mark.line == 0
    assert c.end_mark.line == 24

    assert c["inputs"].start_mark.line == 3
    assert c["inputs"].start_mark.column == 2

    assert c["inputs"]["inp"].start_mark.line == 3
    assert c["inputs"]["inp"].start_mark.column == 7

    assert c["outputs"].start_mark.line == 7

    assert len(c["steps"]) == 2

    assert c["steps"]["untar"].start_mark.line == 13
    assert c["steps"]["untar"].end_mark.line == 19

    assert c["steps"]["untar"]["out"].flow_style
    assert c["steps"]["untar"]["out"][0].start_mark.line == 17
    assert c["steps"]["untar"]["out"][0].start_mark.column == 10

    assert c["steps"]["compile"].start_mark.line == 20
    assert c["steps"]["compile"].end_mark.line == 24


def test_line_number2():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-list.cwl")
    c = parse_cwl_with_line_info(raw_cwl=wf_path.open("r").read())

    assert c["cwlVersion"] == "v1.0"

    assert len(c["steps"]) == 2

    assert c["steps"].start_mark.line == 12
    assert c["steps"].end_mark.line == 24

    assert c["steps"][0].start_mark.line == 12
    assert c["steps"][0].start_mark.column == 4


def test_line_number_salmon():

    wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")
    c = parse_cwl_with_line_info(raw_cwl=wf_path.open("r").read())

    assert c["steps"][0]["run"]["outputs"][0]["doc"].style == ">"
    assert c["steps"][0]["run"]["outputs"][0]["outputBinding"]["glob"].style == "|"
    assert c["steps"][0]["run"]["outputs"][0]["outputBinding"]["glob"].start_mark.line == 672
    assert c["steps"][0]["run"]["outputs"][0]["outputBinding"]["glob"].end_mark.line == 693
