#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .versionmixin import VersionMixin
from ..editing.cwlprocess import CwlProcess


class SBGCwlDoc(VersionMixin, CwlProcess):
    def __init__(self, *args, **kwargs):
        super(SBGCwlDoc, self).__init__(*args, **kwargs)
