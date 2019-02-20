from benten.sbg.jsonmixin import JsonMixin
from benten.editing.cwldoc import CwlDoc


class SBGCwlDoc(JsonMixin, CwlDoc):
    def __init__(self, *args, **kwargs):
        super(SBGCwlDoc, self).__init__(*args, **kwargs)
