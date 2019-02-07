import pathlib

from benten.editing.cwldoc import CwlDoc, list_or_map_w_line_no


current_path = pathlib.Path(__file__).parent


def test_line_number1():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl")

    c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)

    result = {
        s_name: {
            "data": sec,
            "l0": l0,
            "l1": l1
        }
        for s_name, sec, l0, l1 in list_or_map_w_line_no(c.cwl_dict)
    }

    assert result["cwlVersion"]["data"] == "v1.0"
    assert result["cwlVersion"]["l0"] == 0

    assert result["inputs"]["l0"] == 3
    assert result["outputs"]["l0"] == 7

    step_result = {
        s_name: {
            "data": sec,
            "l0": l0,
            "l1": l1
        }
        for s_name, sec, l0, l1 in list_or_map_w_line_no(result["steps"]["data"])
    }

    assert len(step_result) == 2

    assert step_result["untar"]["l0"] == 13
    assert step_result["untar"]["l1"] == 19

    assert step_result["compile"]["l0"] == 20
    assert step_result["compile"]["l1"] == 24


def test_line_number2():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-list.cwl")

    c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)

    result = {
        s_name: {
            "data": sec,
            "l0": l0,
            "l1": l1
        }
        for s_name, sec, l0, l1 in list_or_map_w_line_no(c.cwl_dict)
    }

    assert result["cwlVersion"]["data"] == "v1.0"
    assert result["cwlVersion"]["l0"] == 0

    assert result["inputs"]["l0"] == 3
    assert result["outputs"]["l0"] == 7

    step_result = {
        s_name: {
            "data": sec,
            "l0": l0,
            "l1": l1
        }
        for s_name, sec, l0, l1 in list_or_map_w_line_no(result["steps"]["data"])
    }

    assert len(step_result) == 2

    assert step_result["untar"]["l0"] == 12
    assert step_result["untar"]["l1"] == 19

    assert step_result["compile"]["l0"] == 19
    assert step_result["compile"]["l1"] == 24


def test_line_number_salmon():

    wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")

    c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)

    result = {
        s_name: {
            "data": sec,
            "l0": l0,
            "l1": l1
        }
        for s_name, sec, l0, l1 in list_or_map_w_line_no(c.cwl_dict)
    }

    inputs = {
        s_name: {
            "data": sec,
            "l0": l0,
            "l1": l1
        }
        for s_name, sec, l0, l1 in list_or_map_w_line_no(result["inputs"]["data"])
    }

    assert inputs["reads"]["l0"] == 21
    assert inputs["reads"]["l1"] == 31

    assert inputs["allow_orphans_fmd"]["l0"] == 493
    assert inputs["allow_orphans_fmd"]["l1"] == 504

