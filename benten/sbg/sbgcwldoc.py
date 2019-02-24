from .jsonmixin import JsonMixin
from .versionmixin import VersionMixin
from ..editing.cwldoc import CwlDoc


class SBGCwlDoc(JsonMixin, VersionMixin, CwlDoc):
    def __init__(self, *args, **kwargs):
        super(SBGCwlDoc, self).__init__(*args, **kwargs)
