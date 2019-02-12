from ..editing.cwldoc import CwlDoc


class Tool:
    """In the future, this might scroll to components, or test expressions ..."""

    def __init__(self, cwl_doc: CwlDoc):
        self.cwl_doc = cwl_doc or {}
