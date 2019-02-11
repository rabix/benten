import pathlib

import benten.models.unk as bunk

current_path = pathlib.Path(__file__).parent


def test_parsing_empty_tool():
    empty_wf = ""
    cwl_doc = bunk.CwlDoc(raw_cwl=empty_wf, path=pathlib.Path("./nothing.cwl"))
    u = bunk.Unk(cwl_doc=cwl_doc)

    assert u.cwl_doc == cwl_doc
