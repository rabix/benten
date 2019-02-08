import pathlib

from PySide2.QtWidgets import QGraphicsScene, QGraphicsSceneDragDropEvent
from PySide2.QtCore import Qt, Signal


def is_cwl_document(fname: pathlib.Path):
    if fname.exists():
        # For now, a simple extension check. Later we might load the contents and check for cwlVersion
        return fname.suffix == ".cwl"
    else:
        return False


def paths_to_drop(event: QGraphicsSceneDragDropEvent):
    return (pathlib.Path(f.path()) for f in event.mimeData().urls())


class ProcessScene(QGraphicsScene):
    """We need to subclass this to handle dropping onto the scene"""

    nodes_added = Signal(list)

    def __init__(self, parent):
        super().__init__(parent)

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        if any(is_cwl_document(p) for p in paths_to_drop(event)):
            event.setProposedAction(Qt.CopyAction)
            event.accept()
        else:
            event.setProposedAction(Qt.IgnoreAction)

    def dragMoveEvent(self, event: QGraphicsSceneDragDropEvent):
        if any(is_cwl_document(p) for p in paths_to_drop(event)):
            event.setProposedAction(Qt.CopyAction)
            event.accept()
        else:
            event.setProposedAction(Qt.IgnoreAction)

    def dropEvent(self, event: QGraphicsSceneDragDropEvent):
        wf_list = []
        for p in paths_to_drop(event):
            if is_cwl_document(p):
                event.setProposedAction(Qt.CopyAction)
                wf_list += [p]
                event.accept()

        self.nodes_added.emit(wf_list)
