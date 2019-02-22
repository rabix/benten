import pathlib
import pytest

from benten.editing.lineloader import parse_yaml_with_line_info, coordinates, lookup, reverse_lookup


current_path = pathlib.Path(__file__).parent


def test_basic_load():
    path = pathlib.Path(current_path, "cwl/sample.yaml")
    doc = parse_yaml_with_line_info(raw_cwl=path.open("r").read())

    assert doc["flowstyle dict"].start_mark.line == 2
    assert doc["flowstyle dict"].end_mark.line == 4

    assert coordinates(doc["flowstyle dict"]) == ((2, 16), (4, 41))

    assert coordinates(doc["flowstyle dict"]["ln1"]) == ((2, 22), (2, 47))

    assert coordinates(doc["flowstyle dict"]["ln2"]) == ((2, 57), (2, 70))

    assert coordinates(doc["list"][0]) == ((18, 18), (18, 41))

    assert coordinates(
        doc["level1"]["level2"]["multiline doc preserve newlines"]) == ((24, 37), (30, 0))


def test_lookup():
    path = pathlib.Path(current_path, "cwl/sample.yaml")
    doc = parse_yaml_with_line_info(raw_cwl=path.open("r").read())

    assert lookup(doc, ["list", 1]) == "When you fall"
    assert coordinates(lookup(doc, ["list", 1])) == ((19, 18), (19, 31))

    assert lookup(doc, ["level1", "level2", "list", 3, "list2", 1]) == "When you break"


def test_reverse_lookup():
    path = pathlib.Path(current_path, "cwl/sample.yaml")
    doc = parse_yaml_with_line_info(raw_cwl=path.open("r").read())

    assert reverse_lookup(19, 22, doc) == (["list", 1], "When you fall")

    assert reverse_lookup(26, 22, doc) == \
           (["level1", "level2", "multiline doc preserve newlines"],
            "When you call\n"
            "Who's gonna pay attention\n"
            "To your dreams\n"
            "Who's gonna plug their ears\n"
            "When you scream")

    assert reverse_lookup(2, 64, doc) == (["flowstyle dict", "ln2"], "It's too late")


def test_line_number_dict():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl")
    c = parse_yaml_with_line_info(raw_cwl=wf_path.open("r").read())

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
    c = parse_yaml_with_line_info(raw_cwl=wf_path.open("r").read())

    assert c["cwlVersion"] == "v1.0"

    assert len(c["steps"]) == 2

    assert c["steps"].start_mark.line == 12
    assert c["steps"].end_mark.line == 24

    assert c["steps"][0].start_mark.line == 12
    assert c["steps"][0].start_mark.column == 4


def test_line_number_salmon():

    wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")
    c = parse_yaml_with_line_info(raw_cwl=wf_path.open("r").read())

    assert c["steps"][0]["run"]["outputs"][0]["doc"].style == ">"
    assert c["steps"][0]["run"]["outputs"][0]["outputBinding"]["glob"].style == "|"
    assert c["steps"][0]["run"]["outputs"][0]["outputBinding"]["glob"].start_mark.line == 672
    assert c["steps"][0]["run"]["outputs"][0]["outputBinding"]["glob"].end_mark.line == 693
