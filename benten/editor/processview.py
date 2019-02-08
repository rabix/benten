import pathlib

from PySide2.QtWidgets import QGraphicsScene, QGraphicsSceneDragDropEvent, QGraphicsView
from PySide2.QtCore import Qt, Signal


class ProcessView(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
