import pathlib
import os
import shutil

from benten.editing.cwlprocess import CwlProcess
from benten.models.unk import Unk

current_path = pathlib.Path(__file__).parent
test_dir = "unk-model-test-temp-cwl-dir"


def setup():
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)


def teardown():
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_parsing_empty_unk():

    path = pathlib.Path(test_dir, "nothing.cwl")

    with open(path, "w") as f:
        f.write("")

    cwl_doc = CwlProcess.create_from_file(path)
    cwl_doc.compute_cwl_dict()
    u = Unk(cwl_doc=cwl_doc)

    assert u.cwl_doc == cwl_doc
