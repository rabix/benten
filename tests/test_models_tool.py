import pathlib

import benten.models.tool as btool

current_path = pathlib.Path(__file__).parent


def test_parsing_empty_tool():
    empty_wf = ""
    cwl_doc = btool.CwlDoc(raw_cwl=empty_wf, path=pathlib.Path("./nothing.cwl"))
    t = btool.Tool(cwl_doc=cwl_doc)

    assert t.cwl_doc == cwl_doc
