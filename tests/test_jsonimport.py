import pathlib
import os
import shutil

from benten.sbg.jsonimport import text_format, if_json_convert_to_yaml_and_save
from benten.editing.yamldoc import YamlDoc


current_path = pathlib.Path(__file__).parent
test_dir = "jsonmixin-test-temp-cwl-dir"


def setup():
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)

    shutil.copy(pathlib.Path(current_path, "cwl", "002.nested.inline.sbg.eco", "wf3.json"), test_dir)
    shutil.copy(pathlib.Path(current_path, "cwl", "002.nested.inline.sbg.eco", "wf3.cwl"), test_dir)


def teardown():
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_json_detector():

    assert text_format("") == "yaml"

    assert text_format("\n\n   ") == "yaml"

    assert text_format("\n\n   {") == "json"

    text = pathlib.Path(test_dir, "wf3.cwl").open("r").read()
    assert text_format(text) == "yaml"

    text = pathlib.Path(test_dir, "wf3.json").open("r").read()
    assert text_format(text) == "json"


# todo: handle errors in JSON document
# def test_malformed_json():
#
#     path = pathlib.Path(test_dir, "malformed.json")
#     with open(path, "w") as f:
#         f.write("\n\n{")
#
#     new_path = if_json_convert_to_yaml_and_save(path)
#
#     assert new_path == pathlib.Path(test_dir, "malformed.json.cwl")
#
#     bad_doc = CwlProcess.create_from_file(new_path)
#
#     assert len(bad_doc.yaml_error) == 1
#     assert bad_doc.yaml_error[0].line == 3
#     assert bad_doc.yaml_error[0].column == 0


def test_json_basic():

    # Existing behavior should not change
    wf_path = pathlib.Path(test_dir, "wf3.cwl")
    c = YamlDoc(raw_text=wf_path.open("r").read())
    c.parse_yaml()

    assert c.yaml["label"] == "wf3"
    assert len(c.yaml["steps"]) == 3

    # Now test new behavior with json file
    wf_path = pathlib.Path(test_dir, "wf3.json")

    new_wf_path = if_json_convert_to_yaml_and_save(wf_path)
    assert new_wf_path is not None

    c = YamlDoc(raw_text=new_wf_path.open("r").read())
    c.parse_yaml()

    assert c.yaml["label"] == "wf3"
    assert len(c.yaml["steps"]) == 3

    # SBG tags should be stripped by default
    assert not any(k for k, _ in c.yaml.items() if k[:4] == "sbg:")
    assert not any(k for k, _ in c.yaml["steps"]["wf0"].items() if k[:4] == "sbg:")

    # SBG tags should be kept
    new_wf_path = if_json_convert_to_yaml_and_save(wf_path, strip_sbg_tags=False)
    c = YamlDoc(raw_text=new_wf_path.open("r").read())
    c.parse_yaml()

    assert any(k for k, _ in c.yaml.items() if k[:4] == "sbg:")
    assert any(k for k, _ in c.yaml["steps"]["wf0"].items() if k[:4] == "sbg:")
