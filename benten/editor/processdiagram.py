import pathlib

from PySide2.QtWidgets import QGraphicsScene, QGraphicsSceneDragDropEvent, QGraphicsView
from PySide2.QtCore import Qt

import networkx as nx

import benten.logic.workflow as blwf
import benten.lib as blib


def paths_to_drop(event: QGraphicsSceneDragDropEvent):
    return (pathlib.Path(f.path()) for f in event.mimeData().urls())


class ProcessDiagramScene(QGraphicsScene):
    """We need to subclass this to handle dropping onto the scene"""

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
        for p in paths_to_drop(event):
            if blib.is_cwl_document(p):
                event.setProposedAction(Qt.CopyAction)
                print(p)
                event.accept()


class ProcessDiagramView(QGraphicsView):
    def __init__(self, parent):
        super().__init__(parent)
        self.scene = ProcessDiagramScene(parent)
        self.setAcceptDrops(True)
        self.setScene(self.scene)

    def set_diagram(self, wf: blwf.Workflow):
        G = nx.DiGraph()
        G.add_nodes_from(wf.inputs)
        G.add_nodes_from(wf.steps)
        G.add_nodes_from(wf.outputs)

        G.add_edges_from([
            (
                e.src.node_id or e.src.port_id,
                e.dst.node_id or e.dst.port_id
            )
            for e in wf.connections
        ])

        node_size = [
            10 if (n in wf.inputs or n in wf.outputs) else 100
            for n in G.nodes
        ]

        pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')
