import pathlib
import pytest
import os
import shutil

from benten.editing.documentmanager import DocumentManager
from benten.editing.cwldoc import CwlDoc


current_path = pathlib.Path(__file__).parent
test_dir = "docman-test-temp-cwl-dir"


def setup():
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)

    shutil.copy(pathlib.Path(current_path, "cwl", "002.nested.inline.sbg.eco", "wf3.cwl"), test_dir)


def teardown():
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


def test_basic():
    wf_path = pathlib.Path(test_dir, "wf3.cwl")
    c = CwlDoc(raw_cwl=wf_path.open("r").read(), path=wf_path, inline_path=None)
    doc_man = DocumentManager(cwl_doc=c)

    assert doc_man.raw_cwl == c.raw_cwl
    assert doc_man.path == c.path
    assert doc_man.inline_path == c.inline_path

    assert doc_man.status()["saved"] is True
    assert doc_man.status()["changed_externally"] is False

    c2 = CwlDoc(raw_cwl=c.raw_cwl + "You're cold as ice", path=wf_path, inline_path=None)
    doc_man.set_document(cwl_doc=c2)
    assert doc_man.status()["saved"] is False
    assert doc_man.status()["changed_externally"] is False

    doc_man.save()
    assert doc_man.status()["saved"] is True
    assert doc_man.status()["changed_externally"] is False

    wf_path.open("w").write("You're willing to sacrifice our love")
    assert doc_man.status()["saved"] is False
    assert doc_man.status()["changed_externally"] is True

    c.compute_cwl_dict()
    c3 = CwlDoc(raw_cwl=c.get_raw_cwl_of_nested_inline_step(("wf0",)),
                path=wf_path, inline_path=("wf0",))
    with pytest.raises(RuntimeError):
        _ = DocumentManager(cwl_doc=c3)
