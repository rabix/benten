import networkx as nx

from benten.editor.processscene import ProcessScene
import benten.logic.workflow as blwf


class WorkflowScene(ProcessScene):
    def __init__(self, parent):
        super().__init__(parent)
        self.workflow = None

    def set_workflow(self, wf: blwf.Workflow):
        self.workflow = wf
        self.create_scene()

    def create_scene(self):
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

