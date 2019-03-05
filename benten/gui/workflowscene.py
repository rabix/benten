import pygraphviz as pgv

from PySide2.QtCore import Qt, Slot
from PySide2.QtGui import QBrush, QFont, QPen
from PySide2.QtWidgets import QGraphicsItem, QGraphicsEllipseItem, QGraphicsSimpleTextItem

from .processscene import ProcessScene
from ..models.workflow import Workflow, Step, special_id_for_inputs, special_id_for_outputs
from ..sbg.versionmixin import get_app_info


color_code = {
    "connections": Qt.gray,
    "inputs": Qt.green,
    "outputs": Qt.cyan,
    "CommandLineTool": Qt.gray,
    "ExpressionTool": Qt.yellow,
    "Workflow": Qt.blue,
    "invalid": Qt.white
}


class WFNodeItem(QGraphicsEllipseItem):
    def __init__(self, *args, node_size=30, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_size = node_size
        self.normal_brush = QBrush(kwargs.get("brush"))
        self.selected_brush = QBrush(self.normal_brush.color(), Qt.NoBrush)

    def set_normal_brush(self, normal: QBrush):
        self.normal_brush = normal
        color = normal.color()
        color.setAlpha(75)
        self.selected_brush = QBrush(color)

    def paint(self, *args, **kwargs):
        if self.isSelected():
            self.setBrush(self.selected_brush)
        else:
            self.setBrush(self.normal_brush)
        super(WFNodeItem, self).paint(*args, **kwargs)


class WorkflowScene(ProcessScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.workflow = None
        self.node_size = 30
        self.label_overlay = None

    def set_workflow(self, wf: Workflow):
        self.workflow = wf
        self.create_scene()

    def create_scene(self):
        G = pgv.AGraph(directed=True)

        G.add_node(special_id_for_inputs)
        G.add_nodes_from(self.workflow.steps)
        G.add_node(special_id_for_outputs)

        G.add_edges_from([
            (
                e.src.node_id or special_id_for_inputs,
                e.dst.node_id or special_id_for_outputs
            )
            for e in self.workflow.connections
        ])

        G.layout("dot")

        graph = {
            special_id_for_inputs: {
                "type": "inputs",
                "label": "Input"
            },
            special_id_for_outputs: {
                "type": "outputs",
                "label": "Output"
            }
        }

        def get_label(_step: Step):
            _a_ifo = get_app_info(_step.sub_workflow.id)
            return "\n".join(str(_x) for _x in
                      [_step.id, _a_ifo, "{} ({})".format(_step.process_type,
                                                          _step.sub_workflow.type_str())]
                      if _x is not None)

        for k, step in self.workflow.steps.items():
            graph[k] = {
                "type": step.process_type,
                "label": get_label(step)
            }

        def str_to_pos(_n):
            # https://groups.google.com/forum/#!topic/pygraphviz-discuss/QYXumyw3E-g
            _x, _y = _n.attr["pos"].split(",")
            return float(_x), -float(_y)

        for n in G.nodes():
            graph[n.name]["pos"] = str_to_pos(n)

        pen = QPen(color_code["connections"])
        for e in G.edges():
            p0 = graph[e[0]]["pos"]
            p1 = graph[e[1]]["pos"]
            ln = self.addLine(p0[0], p0[1], p1[0], p1[1])
            ln.setFlag(QGraphicsItem.ItemIsSelectable, True)
            ln.setPen(pen)
            ln.setData(0, (e[0], e[1]))

        for k, v in graph.items():

            p = v["pos"]

            if v["type"] in ["inputs", "outputs"]:
                item = WFNodeItem(p[0] - self.node_size, p[1] - self.node_size / 2,
                                  2 * self.node_size, self.node_size,
                                  node_size=self.node_size)
            else:
                item = WFNodeItem(p[0] - self.node_size / 2, p[1] - self.node_size / 2,
                                  self.node_size, self.node_size,
                                  node_size=self.node_size)

            item.set_normal_brush(QBrush(color_code.get(v["type"], "white")))
            item.setToolTip(v["label"])
            item.setFlag(QGraphicsItem.ItemIsSelectable, True)
            item.setData(0, k)
            self.addItem(item)

            # Add text on top as needed
            if v["type"] == "inputs":
                txt = self.addText(v["label"])
                txt.setPos(p[0] - txt.boundingRect().width()/2, p[1] - txt.boundingRect().height()/2)
            elif v["type"] == "outputs":
                txt = self.addText(v["label"])
                txt.setPos(p[0] - txt.boundingRect().width()/2, p[1] - txt.boundingRect().height()/2)

        self.create_overlay(graph, self.node_size)

    def create_overlay(self, graph, node_size):
        self.label_overlay = QGraphicsSimpleTextItem()
        font = QFont("Helvetica [Cronyx]", 5)
        for k, v in graph.items():
            if v["type"] in ["inputs", "outputs"]: continue
            p = v["pos"]
            txt = QGraphicsSimpleTextItem(v["label"], self.label_overlay)
            txt.setFont(font)
            txt.setPos(p[0] - txt.boundingRect().width() / 2, p[1] - txt.boundingRect().height() - node_size/2)

        self.addItem(self.label_overlay)
        self.label_overlay.setVisible(True)

    @Slot(bool)
    def set_overlay_visible(self, visible=False):
        self.label_overlay.setVisible(visible)
