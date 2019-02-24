from ..editing.cwldoc import CwlDoc


class Base:
    """We don't know what the user intends this to be"""

    def __init__(self, cwl_doc: CwlDoc):
        self.cwl_doc = cwl_doc or {}
        self.id = self.cwl_doc.cwl_dict.get("id", None)
        self.errors = []
