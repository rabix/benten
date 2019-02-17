from PySide2.QtWidgets import QGraphicsView
from PySide2.QtGui import QResizeEvent
from PySide2.QtCore import Qt


class ProcessView(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def resizeEvent(self, event:QResizeEvent):
        super().resizeEvent(event)
        if self.scene():
            self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)
