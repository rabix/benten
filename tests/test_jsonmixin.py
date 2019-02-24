import pathlib
import os
import shutil
import pytest

from benten.sbg.jsonmixin import JsonMixin
from benten.editing.cwldoc import CwlDoc, DocumentError


current_path = pathlib.Path(__file__).parent
test_dir = "jsonmixin-test-temp-cwl-dir"


class SBGCwlDoc(JsonMixin, CwlDoc):
    def __init__(self, *args, **kwargs):
        super(SBGCwlDoc, self).__init__(*args, **kwargs)


def setup():
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)

    shutil.copy(pathlib.Path(current_path, "cwl", "002.nested.inline.sbg.eco", "wf3.json"), test_dir)
    shutil.copy(pathlib.Path(current_path, "cwl", "002.nested.inline.sbg.eco", "wf3.cwl"), test_dir)


def teardown():
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_json_detector():

    assert SBGCwlDoc.detect_cwl_format("") == "yaml"

    assert SBGCwlDoc.detect_cwl_format("\n\n   ") == "yaml"

    assert SBGCwlDoc.detect_cwl_format("\n\n   {") == "json"

    text = pathlib.Path(test_dir, "wf3.cwl").open("r").read()
    assert SBGCwlDoc.detect_cwl_format(text) == "yaml"

    text = pathlib.Path(test_dir, "wf3.json").open("r").read()
    assert SBGCwlDoc.detect_cwl_format(text) == "json"


def test_malformed_json():

    bad_doc = SBGCwlDoc(raw_json="\n\n{", new_path=pathlib.Path(test_dir, "malformed.cwl"))

    assert len(bad_doc.yaml_error) == 1
    assert bad_doc.yaml_error[0].line == 3
    assert bad_doc.yaml_error[0].column == 0


def test_json_basic():

    # Existing behavior should not change
    wf_path = pathlib.Path(test_dir, "wf3.cwl")
    c = SBGCwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)
    c.compute_cwl_dict()

    assert c.cwl_dict["label"] == "wf3"
    assert len(c.cwl_dict["steps"]) == 3

    # Now test new behavior with json file
    wf_path = pathlib.Path(test_dir, "wf3.json")
    new_wf_path = pathlib.Path(test_dir, "wf3.cwl")

    with pytest.raises(RuntimeError):
        _ = SBGCwlDoc(raw_json=wf_path.open("r").read())

    c = SBGCwlDoc(raw_json=wf_path.open("r").read(), new_path=new_wf_path, inline_path=None)
    c.compute_cwl_dict()

    assert c.cwl_dict["label"] == "wf3"
    assert len(c.cwl_dict["steps"]) == 3

    # SBG tags should be stripped by default
    assert not any(k for k, _ in c.cwl_dict.items() if k[:4] == "sbg:")
    assert not any(k for k, _ in c.cwl_dict["steps"]["wf0"].items() if k[:4] == "sbg:")

    # SBG tags should be kept
    c = SBGCwlDoc(raw_json=wf_path.open("r").read(), new_path=new_wf_path, strip_sbg_tags=False)
    c.compute_cwl_dict()

    assert any(k for k, _ in c.cwl_dict.items() if k[:4] == "sbg:")
    assert any(k for k, _ in c.cwl_dict["steps"]["wf0"].items() if k[:4] == "sbg:")
