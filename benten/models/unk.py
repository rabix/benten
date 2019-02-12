from ..editing.cwldoc import CwlDoc


class Unk:
    """We don't know what the user intends this to be"""

    def __init__(self, cwl_doc: CwlDoc):
        self.cwl_doc = cwl_doc or {}
