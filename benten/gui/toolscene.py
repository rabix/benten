from PySide2.QtGui import QFont

from .processscene import ProcessScene
from ..models.tool import Tool


class ToolScene(ProcessScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.tool = None

    def set_tool(self, tool: Tool):
        self.tool = tool
        self.create_scene()

    def create_scene(self):
        """Might be more sophisticated in the future"""
        pt = self.tool.cwl_doc.process_type()
        self.addText(pt, QFont(family="Helvetica", pointSize=6))
