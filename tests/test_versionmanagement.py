#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
import pytest

pytest.skip("Skipping test until refactor is complete", allow_module_level=True)

import benten.sbg.versionmanagement as sam
from benten.editing.yamlview import YamlView


current_path = pathlib.Path(__file__).parent


def test_app_version():

    app_info = sam.get_app_info(None)
    assert app_info is None

    app_id = "In-fact-it-was-a-little-bit-frightening"
    app_info = sam.get_app_info(app_id)
    assert app_info is None

    app_id = "But/they/fought/with/expert/timing"
    app_info = sam.get_app_info(app_id)
    assert app_info is None

    app_id = "They-were/funky-China-men/from/funky-Chinatown"
    app_info = sam.get_app_info(app_id)
    assert app_info is None

    app_id = "admin/sbg-public-data/salmon-index-0-9-1/12"
    app_info = sam.get_app_info(app_id)

    assert app_info.owner == "admin"
    assert app_info.project == "sbg-public-data"
    assert app_info.name == "salmon-index-0-9-1"
    assert app_info.version == 12
    assert app_info.local_edits is False
    assert str(app_info) == "salmon-index-0-9-1 (v:12)"

    app_id = app_id + sam.file_not_pushed_suffix
    app_info = sam.get_app_info(app_id)
    assert app_info.local_edits is True
    assert str(app_info) == "salmon-index-0-9-1 (v:12*)"


@pytest.mark.skip(reason="SBG integration will be worked on next")
def test_repomixin_basic():

    class SBGCwlDoc(sam.VersionMixin, CwlProcess):
        def __init__(self, *args, **kwargs):
            super(SBGCwlDoc, self).__init__(*args, **kwargs)

    wf_path = pathlib.Path(current_path, "cwl/002.nested.inline.sbg.eco/wf3.cwl")
    c = SBGCwlDoc.create_from_file(wf_path)

    assert c.app_info.owner == "kghose"
    assert c.app_info.project == "benten-demo"
    assert c.app_info.version == 1
