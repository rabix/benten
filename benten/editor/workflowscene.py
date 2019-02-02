import pygraphviz as pgv

from PySide2.QtCore import Qt, QRectF, QPointF
from PySide2.QtGui import QPen, QBrush, QColor
from PySide2.QtWidgets import QGraphicsEllipseItem

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
        G.add_nodes_from(self.workflow.inputs, type="input")
        G.add_nodes_from(self.workflow.steps, type="step")
        G.add_nodes_from(self.workflow.outputs, type="output")

        G.add_edges_from([
            (
                e.src.node_id or e.src.port_id,
                e.dst.node_id or e.dst.port_id
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

        base_node_size = 50
        for k, v in graph.items():
            if v["type"] == "step":
                node_size = base_node_size
            else:
                node_size = base_node_size / 10

            p = v["pos"]

            ellipse = QGraphicsEllipseItem(p[0] - node_size/2, p[1] - node_size/2, node_size, node_size)
            ellipse.setBrush(QBrush(Qt.black if v["type"] == "step" else Qt.gray))
            ellipse.setVisible(True)
            self.addItem(ellipse)

        for e in G.edges():
            p0 = graph[e[0]]["pos"]
            p1 = graph[e[1]]["pos"]
            self.addLine(p0[0], p0[1], p1[0], p1[1])

        print(self.sceneRect())

    def create_scene2(self):
        G = nx.DiGraph()
        G.add_nodes_from(self.workflow.inputs)
        G.add_nodes_from(self.workflow.steps)
        G.add_nodes_from(self.workflow.outputs)

        G.add_edges_from([
            (
                e.src.node_id or e.src.port_id,
                e.dst.node_id or e.dst.port_id
            )
            for e in self.workflow.connections
        ])

        node_size = [
            10 if (n in self.workflow.inputs or n in self.workflow.outputs) else 100
            for n in G.nodes
        ]

        pos = nx.drawing.nx_agraph.graphviz_layout(G, prog='dot')

        xmin = min((p[0] for p in pos.values()))
        xmax = max((p[0] for p in pos.values()))
        ymin = min((p[1] for p in pos.values()))
        ymax = max((p[1] for p in pos.values()))

        x_range = xmax - xmin
        y_range = ymax - ymin

        node_size2 = 100
        for k, v in pos.items():
            ellipse = QGraphicsEllipseItem(v[0] - node_size2/2, v[1] - node_size2/2, node_size2, node_size2)
            ellipse.setBrush(QBrush(Qt.black))
            ellipse.setVisible(True)
            self.addItem(ellipse)

        print(self.sceneRect())
