#  Copyright (c) 2019 Seven Bridges. See LICENSE

import os
import shutil
import sys
from pathlib import Path as P
import configparser
import json

from pkg_resources import resource_stream
from .cwl.specification import parse_schema

import logging
logger = logging.getLogger(__name__)

supported_versions = ["v1.0", "v1.1", "v1.2.0-dev1", "v1.2.0-dev3", "v1.2.0"]

sbg_config_dir = P("sevenbridges", "benten")

def get_user_dir():
    # This logic should be synchronized with
    # vscode-client/src/extension.ts: get_user_dir()
    return (os.environ.get("APPDATA") or
        os.environ.get("XDG_DATA_HOME") or
        (P(P.home(), 'Library', 'Preferences')
         if sys.platform == 'darwin'
         else P(P.home(), '.local', 'share')))

class Configuration(configparser.ConfigParser):
    def __init__(self):
        super().__init__()

        user_dir = get_user_dir()
        self.cfg_path = P(user_dir, sbg_config_dir)
        self.log_path = P(user_dir, sbg_config_dir, "logs")
        self.scratch_path = P(user_dir, sbg_config_dir, "scratch")

        if not self.cfg_path.exists():
            self.cfg_path.mkdir(parents=True)

        if not self.log_path.exists():
            self.log_path.mkdir(parents=True)

        if not self.scratch_path.exists():
            self.scratch_path.mkdir(parents=True)

        self.lang_models = {}

    # We do this separately to give the caller a chance to set up logging
    def initialize(self):
        # TODO: allow multiple language specifications
        logging.info("Loading language model ...")
        self._load_language_files()

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

    def _load_language_files(self):
        for version in supported_versions:
            rsc = resource_stream("benten_schemas", "schema-%s.json" % (version))
            schema = json.load(rsc)
            rsc.close()
            self.lang_models[version] = parse_schema(schema)
            logger.info(f"Loaded language schema {version}")
