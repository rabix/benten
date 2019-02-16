import pathlib

from benten.editing.cwldoc import CwlDoc
from benten.models.unk import Unk

current_path = pathlib.Path(__file__).parent


def test_parsing_empty_tool():
    empty_wf = ""
    cwl_doc = CwlDoc(raw_cwl=empty_wf, path=pathlib.Path("./nothing.cwl"))
    cwl_doc.compute_cwl_dict()
    u = Unk(cwl_doc=cwl_doc)

    assert u.cwl_doc == cwl_doc
