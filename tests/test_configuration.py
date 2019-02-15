import os
import shutil
import pathlib

from benten.configuration import Configuration


test_dir = "./benten-test-config"


def setup():
    # First we make sure there is no existing config file, say from a previous run
    shutil.rmtree(pathlib.Path(test_dir), ignore_errors=True)


def teardown():
    shutil.rmtree(pathlib.Path(test_dir), ignore_errors=True)


# monkey patch is amazing!
# https://docs.pytest.org/en/latest/monkeypatch.html
# https://holgerkrekel.net/2009/03/03/monkeypatching-in-unit-tests-done-right/
def test_basic(monkeypatch):
    monkeypatch.setitem(os.environ, "XDG_CONFIG_HOME", test_dir)
    monkeypatch.setitem(os.environ, "XDG_DATA_HOME", test_dir)

    # test creation of config dirs and default file
    config = Configuration()

    assert "files" in config.sections()
    assert "autosave" in config["files"]

    # test saving and loading of existing file
    config["files"]["autosave"] = "False"
    config.save()

    config.load()
    assert not config.getboolean("files", "autosave")
