import pathlib

from benten.sbg.sbgcwldoc import SBGCwlDoc


current_path = pathlib.Path(__file__).parent


def test_basic():
    wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")
    c = SBGCwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)

    c.compute_cwl_dict()
    cwl = c.cwl_dict

    assert c.process_type() == "Workflow"

    assert cwl["steps"]["Salmon_Quant___Reads"]["in"]["salmon_index_archive"].start_line == 2093
    assert cwl["steps"]["Salmon_Quant___Reads"]["in"]["salmon_index_archive"]["source"] == "Salmon_Index/salmon_index_archive"
