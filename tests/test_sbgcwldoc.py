import pathlib

from benten.sbg.sbgcwldoc import SBGCwlDoc


current_path = pathlib.Path(__file__).parent


def test_basic():
    wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")
    c = SBGCwlDoc.create_from_file(wf_path)

    c.compute_cwl_dict()
    cwl = c.cwl_dict

    assert c.type() == "Workflow"

    assert cwl["steps"]["Salmon_Quant___Reads"]["in"]["salmon_index_archive"].start.line == 2093
    assert cwl["steps"]["Salmon_Quant___Reads"]["in"]["salmon_index_archive"]["source"] == "Salmon_Index/salmon_index_archive"
