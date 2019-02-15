"""Provide interfaces to manage SBG contexts and pushing to SBG app store"""
import pathlib

import sevenbridges as sbg

from ..configuration import Configuration, configparser, default_credentials_file


class ProfileError(Exception):
    def __init__(self, profile_name):
        self.profile_name = profile_name


class Profiles:
    def __init__(self, config: Configuration):
        self.config = config

        self.profile_parser: configparser.ConfigParser = configparser.ConfigParser()
        self.credentials_file = pathlib.Path(
            self.config.get("sbg", "credentials_file", fallback=str(default_credentials_file)))

        self.profiles = []

        if self.credentials_file.exists():
            self.profile_parser.read(self.credentials_file)
            self.profiles = self.profile_parser.sections()

    def __getitem__(self, item):
        if item not in self.profiles:
            raise KeyError("This is a bug, please report it")
        else:
            try:
                return sbg.Api(url=self.profile_parser.get(item, "api_endpoint"),
                               token=self.profile_parser.get(item, "auth_token"))
            except configparser.NoOptionError as e:
                raise ProfileError(item)
