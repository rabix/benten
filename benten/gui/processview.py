from PySide2.QtWidgets import QGraphicsView


class ProcessView(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAcceptDrops(True)
