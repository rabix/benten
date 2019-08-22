"""Provide interfaces to manage SBG contexts and pushing to SBG app store"""
#  Copyright (c) 2019 Seven Bridges. See LICENSE

import sevenbridges as sbg

from ..version import __version__
from ..configuration import Configuration, configparser


class ProfileError(Exception):
    def __init__(self, profile_name):
        self.profile_name = profile_name


class Profiles:
    def __init__(self, config: Configuration):
        self.config = config

        self.profile_parser: configparser.ConfigParser = configparser.ConfigParser()
        self.credentials_file = self.config.getpath("sbg", "credentials_file")

        self.profiles = []

        if self.credentials_file.exists():
            self.profile_parser.read(self.credentials_file)
            self.profiles = self.profile_parser.sections()

    def __getitem__(self, item):
        if item not in self.profiles:
            raise KeyError("This is a bug, please report it")
        else:
            try:
                api = sbg.Api(url=self.profile_parser.get(item, "api_endpoint"),
                              token=self.profile_parser.get(item, "auth_token"))
                # Least disruptive way to add in our user agent
                api.headers["User-Agent"] = "Benten/{} via {}".\
                    format(__version__, api.headers["User-Agent"])
                return api
            except configparser.NoOptionError as e:
                raise ProfileError(item)
