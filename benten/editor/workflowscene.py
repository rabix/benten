from enum import IntEnum

import pygraphviz as pgv

from PySide2.QtCore import Qt, QRectF, QPointF
from PySide2.QtGui import QPen, QBrush, QColor, QPolygonF
from PySide2.QtWidgets import QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsItem

from benten.editor.processscene import ProcessScene
import benten.models.workflow as blwf


class WorkflowScene(ProcessScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.workflow = None

    def set_workflow(self, wf: blwf.Workflow):
        self.workflow = wf
        self.create_scene()

    def create_scene(self):
        G = pgv.AGraph(directed=True)
        G.add_node("inputs", type="inputs")
        G.add_nodes_from(self.workflow.steps, type="step")
        G.add_node("outputs", type="outputs")

        G.add_edges_from([
            (
                e.src.node_id or "inputs",
                e.dst.node_id or "outputs"
            )
            for e in self.workflow.connections
        ])

        G.layout("dot")
        # from IPython import embed; embed()

        graph = {
            n.name: {
                # https://groups.google.com/forum/#!topic/pygraphviz-discuss/QYXumyw3E-g
                "pos": [float(x) for x in n.attr["pos"].split(",")],
                "type": n.attr["type"]
            }
            for n in G.nodes()
        }

        for e in G.edges():
            p0 = graph[e[0]]["pos"]
            p1 = graph[e[1]]["pos"]
            ln = self.addLine(p0[0], p0[1], p1[0], p1[1])
            ln.setFlag(QGraphicsItem.ItemIsSelectable, True)
            ln.setData(0, (e[0], e[1]))

        node_size = 30
        for k, v in graph.items():

            p = v["pos"]

            if v["type"] == "step":
                item = QGraphicsEllipseItem(p[0] - node_size/2, p[1] - node_size/2, node_size, node_size)
            elif v["type"] == "inputs":
                item = self.addPolygon(QPolygonF([QPointF(p[0], p[1]),
                                                  QPointF(p[0] + node_size/2, p[1] + node_size/2),
                                                  QPointF(p[0] - node_size/2, p[1] + node_size/2)]))
            else:
                item = self.addPolygon(QPolygonF([QPointF(p[0], p[1] - node_size/2),
                                                  QPointF(p[0] + node_size/2, p[1]),
                                                  QPointF(p[0] - node_size/2, p[1])]))

            item.setBrush(QBrush(Qt.gray))
            item.setToolTip(k)
            item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            item.setData(0, k)
            self.addItem(item)

        print(self.sceneRect())
