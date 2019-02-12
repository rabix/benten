from PySide2.QtGui import QFont

from .processscene import ProcessScene


class UnkScene(ProcessScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.addText("Unknown process type", QFont(family="Helvetica", pointSize=6))
