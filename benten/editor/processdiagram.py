from PySide2.QtWidgets import QGraphicsScene, QGraphicsView


class ProcessDiagram(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)

