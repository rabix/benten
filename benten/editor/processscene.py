import pathlib

from PySide2.QtWidgets import QGraphicsScene, QGraphicsSceneDragDropEvent
from PySide2.QtCore import Qt, Signal

import benten.lib as blib


def paths_to_drop(event: QGraphicsSceneDragDropEvent):
    return (pathlib.Path(f.path()) for f in event.mimeData().urls())


class ProcessScene(QGraphicsScene):
    """We need to subclass this to handle dropping onto the scene"""

    nodes_added = Signal(list)

    def __init__(self, parent):
        super().__init__(parent)

    def dragEnterEvent(self, event: QGraphicsSceneDragDropEvent):
        if any(blib.is_cwl_document(p) for p in paths_to_drop(event)):
            event.setProposedAction(Qt.CopyAction)
            event.accept()
        else:
            event.setProposedAction(Qt.IgnoreAction)

    def dragMoveEvent(self, event: QGraphicsSceneDragDropEvent):
        if any(blib.is_cwl_document(p) for p in paths_to_drop(event)):
            event.setProposedAction(Qt.CopyAction)
            event.accept()
        else:
            event.setProposedAction(Qt.IgnoreAction)

    def dropEvent(self, event: QGraphicsSceneDragDropEvent):
        wf_list = []
        for p in paths_to_drop(event):
            if blib.is_cwl_document(p):
                event.setProposedAction(Qt.CopyAction)
                wf_list += [p]
                event.accept()

        self.nodes_added.emit(wf_list)
