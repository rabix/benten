import pathlib

config_dir = pathlib.Path(pathlib.Path.home(), ".sevenbridges", "benten")
if not config_dir.exists():
    config_dir.mkdir(parents=True)

template_dir = pathlib.Path(config_dir, "cwl-templates")
if not template_dir.exists():
    template_dir.mkdir(parents=True)
