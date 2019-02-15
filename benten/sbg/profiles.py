"""Provide interfaces to manage SBG contexts and pushing to SBG app store"""
import pathlib

import sevenbridges as sbg

from ..configuration import Configuration, configparser


class Profiles:
    def __init__(self, config: Configuration):
        self.config = config

        self.profile_parser = configparser.ConfigParser()
        self.credentials_file = pathlib.Path(
            self.config.get("credentials_file", pathlib.Path("~/.sevenbridges/credentials").resolve()))

        self.profiles = []

        if self.credentials_file.exists():
            self.profile_parser.read(self.credentials_file)
            self.profiles = self.profile_parser.sections()

    def __getitem__(self, item):
        if item not in self.profiles:
            raise KeyError
        else:
            return sbg.Api(config=sbg.Config(profile=item))
