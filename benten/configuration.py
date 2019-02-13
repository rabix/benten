import os
import pathlib
import configparser

sbg_config_dir = pathlib.Path("sevenbridges", "benten")


# https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

xdg_config_dir = {
    "env": "XDG_CONFIG_HOME",
    "default": pathlib.Path(pathlib.Path.home(), ".config")
}

# There is a raging debate on this and people want to add a new field to the XDG spec
# Me, I think logs are user data ...
xdg_log_dir = {
    "env": "XDG_DATA_HOME",
    "default": pathlib.Path(pathlib.Path.home(), ".local", "share")
}


class Configuration(configparser.ConfigParser):
    def __init__(self):
        super().__init__()

        self.cfg_file = pathlib.Path(os.getenv(xdg_config_dir["env"], xdg_config_dir["default"]),
                                     sbg_config_dir, pathlib.Path("config.ini"))

        self.log_path = pathlib.Path(os.getenv(xdg_log_dir["env"], xdg_log_dir["default"]),
                                     sbg_config_dir, pathlib.Path("logs"))

        if not self.log_path.exists():
            self.log_path.mkdir(parents=True)

        if not self.cfg_file.exists():
            self.cfg_file.parent.mkdir(parents=True, exist_ok=True)
            self.create_default_config_file()

        self.load()

    def create_default_config_file(self):
        cfg = configparser.ConfigParser()
        cfg["files"] = {
            "autosave": True,
            "autoload": False
        }
        with open(self.cfg_file, "w") as f:
            cfg.write(f)

    def load(self):
        self.read(self.cfg_file)

    def save(self):
        self.write(self.cfg_file.open("w"))
