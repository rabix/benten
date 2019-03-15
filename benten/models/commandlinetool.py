from .base import Base
from .editmixin import EditMixin
from .clteditmixin import CltEditMixin


class CommandLineTool(CltEditMixin, EditMixin, Base):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_sections = ["cwlVersion", "class", "inputs", "outputs", "steps"]
        self.parse_sections(required_sections)
