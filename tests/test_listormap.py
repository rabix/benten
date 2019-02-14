import pathlib
import pytest

from benten.editing.listormap import CWLList, parse_cwl_to_lom


current_path = pathlib.Path(__file__).parent


def test_basics():
    l = CWLList([0, 1, 2, 3, 4])

    assert l.plain_list

    with pytest.raises(RuntimeError):
        _ = l.get("k")

    assert l[2] == 2

    assert 2 in l

    l = CWLList([
        {"id": "a", "value": 1},
        {"id": "b", "value": 2},
        {"id": "c", "value": 3},
    ])

    assert l.get("a") == {"id": "a", "value": 1}
    assert l.get("d") is None

    with pytest.raises(KeyError):
        _ = l["d"]

    assert "c" in l


def test_line_number1():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl")

    c = parse_cwl_to_lom(raw_cwl=wf_path.open("r").read())

    assert c["cwlVersion"] == "v1.0"

    assert c["inputs"].start_line == 3
    assert c["outputs"].start_line == 7

    assert len(c["steps"]) == 2

    assert c["steps"]["untar"].start_line == 13
    assert c["steps"]["untar"].end_line == 19

    assert c["steps"]["compile"].start_line == 20
    assert c["steps"]["compile"].end_line == 24


def test_line_number2():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-list.cwl")

    c = parse_cwl_to_lom(raw_cwl=wf_path.open("r").read())

    assert c["cwlVersion"] == "v1.0"

    assert c["inputs"].start_line == 3
    assert c["outputs"].start_line == 7

    assert len(c["steps"]) == 2

    assert c["steps"]["untar"].start_line == 12
    assert c["steps"]["untar"].end_line == 19

    assert c["steps"]["compile"].start_line == 19
    assert c["steps"]["compile"].end_line == 24


def test_line_number_salmon():

    wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")

    c = parse_cwl_to_lom(raw_cwl=wf_path.open("r").read())

    assert c["inputs"]["reads"].start_line == 21
    assert c["inputs"]["reads"].end_line == 31

    assert c["inputs"]["allow_orphans_fmd"].start_line == 493
    assert c["inputs"]["allow_orphans_fmd"].end_line == 504
