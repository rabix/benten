"""Extends configuration to add an SBG api instance.

We need the API instance in many places and since we already propagate the configuration object
everywhere we choose to ride on this"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from ..sbg.profiles import Profiles, Configuration


class SBConfig(Configuration):
    def __init__(self):
        super().__init__()
        self.api = None

    def set_profile(self, profile):
        self.api = Profiles(self)[profile]

        if "sbg" not in self.last_session.sections():
            self.last_session["sbg"] = {}
        self.last_session["sbg"]["context"] = profile
