import pathlib

from benten.editing.cwldoc import CwlDoc
from benten.models.tool import Tool

current_path = pathlib.Path(__file__).parent


def test_parsing_empty_tool():
    empty_wf = ""
    cwl_doc = CwlDoc(raw_cwl=empty_wf, path=pathlib.Path("./nothing.cwl"))
    cwl_doc.compute_cwl_dict()
    t = Tool(cwl_doc=cwl_doc)

    assert t.cwl_doc == cwl_doc
