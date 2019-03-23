import os
import shutil
from pathlib import Path as P
import configparser

sbg_config_dir = P("sevenbridges", "benten")


# https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html

xdg_config_dir = {
    "env": "XDG_CONFIG_HOME",
    "default": P(P.home(), ".config")
}

# There is a raging debate on this and people want to add a new field to the XDG spec
# Me, I think logs are user data ...
xdg_log_dir = {
    "env": "XDG_DATA_HOME",
    "default": P(P.home(), ".local", "share")
}

default_config_data_dir = P(P(__file__).parent, "000.package.data")


class Configuration(configparser.ConfigParser):
    def __init__(self):
        super().__init__()

        self.cfg_path = P(os.getenv(xdg_config_dir["env"], xdg_config_dir["default"]), sbg_config_dir)
        self.log_path = P(os.getenv(xdg_log_dir["env"], xdg_log_dir["default"]), sbg_config_dir, "logs")
        self.path = P(self.cfg_path, "config.ini")

        if not self.log_path.exists():
            self.log_path.mkdir(parents=True)

        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.create_default_config_file()

        self.load()

        self.copy_missing_templates()

    # https://stackoverflow.com/questions/1611799/preserve-case-in-configparser
    def optionxform(self, optionstr):
        return optionstr

    def getpath(self, section, option):
        return self._resolve_path(P(self.get(section, option)))

    def _resolve_path(self, path: P):
        """Paths in the config file can be absolute or relative. Absolute paths are left untouched
        relative paths are resolved relative to the configuration file location"""
        path = path.expanduser()
        if path.is_absolute():
            return path
        else:
            return P(self.cfg_path, path)

    def create_default_config_file(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        shutil.copy(P(default_config_data_dir, "config.ini"), self.path)

    def copy_missing_templates(self):
        cwl_default_template_dir = P(default_config_data_dir, "cwl-templates")
        cwl_template_dir = self._resolve_path(P(self.get("cwl", "template_dir")))
        for dirpath, dirnames, filenames in os.walk(cwl_default_template_dir):
            for name in filenames:
                src_tplt = P(dirpath, name)
                dst_tplt = P(cwl_template_dir, src_tplt.relative_to(cwl_default_template_dir))
                if dst_tplt.exists():
                    continue
                else:
                    os.makedirs(os.path.dirname(dst_tplt), exist_ok=True)
                    shutil.copy(src_tplt, dst_tplt)

    def load(self):
        # https://docs.python.org/3/library/configparser.html#configparser.ConfigParser.read
        self.read_file(P(default_config_data_dir, "config.ini").open("r"))
        self.read(self.path)

    # We don't do this because we don't want to mess with the user's original formatting
    # def save(self):
    #     self.write(self.path.open("w"))
