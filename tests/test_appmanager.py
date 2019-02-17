import pytest

import benten.sbg.appmanager as sam


def test_app_version():

    app_info = sam.get_app_info(None)
    assert isinstance(app_info, sam.NotSBGApp)

    app_id = "In-fact-it-was-a-little-bit-frightening"
    app_info = sam.get_app_info(app_id)
    assert isinstance(app_info, sam.NotSBGApp)
    assert str(app_info) == ""

    app_id = "But/they/fought/with/expert/timing"
    app_info = sam.get_app_info(app_id)
    assert isinstance(app_info, sam.NotSBGApp)

    app_id = "They-were/funky-China-men/from/funky-Chinatown"
    app_info = sam.get_app_info(app_id)
    assert isinstance(app_info, sam.NotSBGApp)

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
