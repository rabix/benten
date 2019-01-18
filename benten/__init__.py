import pathlib

config_dir = pathlib.Path(pathlib.Path.home(), ".sevenbridges", "benten")
if not config_dir.exists():
    config_dir.mkdir(parents=True)
