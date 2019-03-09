from .base import Base, CwlProcess
from .editmixin import EditMixin
from .clteditmixin import CltEditMixin


class CommandLineTool(CltEditMixin, EditMixin, Base):

    def __init__(self, cwl_doc: CwlProcess):
        super().__init__(cwl_doc=cwl_doc)

        required_sections = ["cwlVersion", "class", "inputs", "outputs", "steps"]
        self.parse_sections(required_sections)
