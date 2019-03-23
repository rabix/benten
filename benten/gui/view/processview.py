from PySide2.QtWidgets import QGraphicsView
from PySide2.QtGui import QResizeEvent, QWheelEvent
from PySide2.QtCore import Qt


class ProcessView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.custom_zoom = False

        self.process_model = None

    def resizeEvent(self, event:QResizeEvent):
        super().resizeEvent(event)
        if self.scene() and not self.custom_zoom:
            self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)

    def reset_zoom(self):
        self.custom_zoom = False
        self.fitInView(self.scene().sceneRect(), Qt.KeepAspectRatio)

    def wheelEvent(self, event: QWheelEvent):
        if self.scene():
            self.custom_zoom = True
            scale = 1 + event.delta() / 500
            self.scale(scale, scale)
