import os
import shutil
import pathlib

from benten.configuration import Configuration


# monkey patch is amazing!
# https://docs.pytest.org/en/latest/monkeypatch.html
# https://holgerkrekel.net/2009/03/03/monkeypatching-in-unit-tests-done-right/
def test_basic(monkeypatch):
    monkeypatch.setitem(os.environ, "XDG_CONFIG_HOME", "./benten-test-config")
    monkeypatch.setitem(os.environ, "XDG_DATA_HOME", "./benten-test-config")

    # First we make sure there is no existing config file, say from a previous run
    shutil.rmtree(pathlib.Path("./benten-test-config"), ignore_errors=True)

    # test creation of config dirs and default file
    config = Configuration()

    assert "files" in config.sections()
    assert "autosave" in config["files"]

    # test saving and loading of existing file
    config["files"]["autosave"] = "False"
    config.save()

    config.load()
    assert not config.getboolean("files", "autosave")
