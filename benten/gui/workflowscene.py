import pygraphviz as pgv

from PySide2.QtCore import Qt, QPointF
from PySide2.QtGui import QBrush, QPen, QPolygonF
from PySide2.QtWidgets import QGraphicsEllipseItem, QGraphicsItem, QGraphicsPolygonItem

from .processscene import ProcessScene
from ..models.workflow import Workflow


color_code = {
    "inputs": Qt.green,
    "outputs": Qt.red,
    "CommandLineTool": Qt.gray,
    "ExpressionTool": Qt.yellow,
    "Workflow": Qt.blue,
    "invalid": Qt.white
}


class WorkflowScene(ProcessScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.workflow = None

    def set_workflow(self, wf: Workflow):
        self.workflow = wf
        self.create_scene()

    def create_scene(self):
        G = pgv.AGraph(directed=True)
        G.add_node("inputs", type="inputs")
        for k, step in self.workflow.steps.items():
            G.add_node(k, type=step.process_type)
        G.add_node("outputs", type="outputs")

        G.add_edges_from([
            (
                e.src.node_id or "inputs",
                e.dst.node_id or "outputs"
            )
            for e in self.workflow.connections
        ])

        G.layout("dot")

        def str_to_pos(_n):
            # https://groups.google.com/forum/#!topic/pygraphviz-discuss/QYXumyw3E-g
            _x, _y = _n.attr["pos"].split(",")
            return float(_x), -float(_y)

        graph = {
            n.name: {
                "pos": str_to_pos(n),
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

            if v["type"] in ["inputs", "outputs"]:
                item = QGraphicsEllipseItem(p[0] - node_size, p[1] - node_size/2, 2 * node_size, node_size)
            else:
                item = QGraphicsEllipseItem(p[0] - node_size/2, p[1] - node_size/2, node_size, node_size)

            # item.setPen(QPen(Qt.gray))
            item.setBrush(QBrush(color_code.get(v["type"], "white")))
            item.setToolTip(k)
            item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            item.setData(0, k)
            self.addItem(item)

            # Add text on top as needed
            if v["type"] == "inputs":
                txt = self.addText("inputs")
                txt.setPos(p[0] - txt.boundingRect().width()/2, p[1] - txt.boundingRect().height()/2)
            elif v["type"] == "outputs":
                txt = self.addText("outputs")
                txt.setPos(p[0] - txt.boundingRect().width()/2, p[1] - txt.boundingRect().height()/2)
