"""This presents us with a simple hideable dialog in the workflow mode that allows us to
quickly wire-up the workflow based on available inputs and outputs between a pair of nodes.
______________   ______________
| src node |v|   |   port   |v|
‾‾‾‾‾‾‾‾‾‾‾‾‾‾   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾
______________   ______________  ___
| dst node |v|   |   port   |v|  |+|
‾‾‾‾‾‾‾‾‾‾‾‾‾‾   ‾‾‾‾‾‾‾‾‾‾‾‾‾‾  ‾‾‾

* Auto complete for [inputs, outputs, steps]
* second level autocomplete for ports
* We are allowed to enter new ports for inputs, outputs (that are not on the list)

- Have four boxes + "connect" button that you can cycle through with tab
- auto complete in each box
- Source and destination boxes retain original id since we often make connections in batches


"""
from PySide2.QtWidgets import \
    (QWidget, QComboBox, QLabel, QPushButton, QTableWidget, QAbstractItemView, QHBoxLayout,
     QVBoxLayout, QGridLayout,  QSplitter, QShortcut, QGraphicsSceneMouseEvent)
from PySide2.QtCore import Slot, Signal

from ...models.workflow import Workflow, special_id_for_inputs, special_id_for_outputs


class WiringUpWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.src_node = QComboBox(self)
        self.src_node.setEditable(True)
        self.src_port = QComboBox(self)
        self.src_port.setEditable(True)

        self.dst_node = QComboBox(self)
        self.dst_node.setEditable(True)
        self.dst_port = QComboBox(self)
        self.dst_port.setEditable(True)

        self.button = QPushButton("+")
        self.button.setMaximumWidth(50)

        self.src_node.activated.connect(self.src_node_selected)
        self.dst_node.activated.connect(self.dst_node_selected)

        layout = QGridLayout()
        self.setLayout(layout)

        layout.addWidget(self.src_node, 0, 0)
        layout.addWidget(self.src_port, 0, 1)
        layout.addWidget(self.dst_node, 1, 0)
        layout.addWidget(self.dst_port, 1, 1)
        layout.addWidget(self.button, 1, 2)
        layout.setHorizontalSpacing(0)
        layout.setVerticalSpacing(0)
        layout.setMargin(0)

        self.setMaximumHeight(50)
        self.setVisible(False)

        self.workflow = None

    def set_tab_order(self):
        QWidget.setTabOrder(self.src_node, self.src_port)
        QWidget.setTabOrder(self.src_port, self.dst_node)
        QWidget.setTabOrder(self.dst_node, self.dst_port)
        QWidget.setTabOrder(self.dst_port, self.button)
        QWidget.setTabOrder(self.button, self.src_node)

    def set_workflow(self, workflow: Workflow):
        self.workflow = workflow

        self.src_node.addItems([special_id_for_inputs] +
                               list(self.workflow.steps.keys()) +
                               [special_id_for_outputs])

    @Slot()
    def src_node_selected(self):
        step_id = self.src_node.currentText()
        port_ids = []
        if step_id == special_id_for_inputs:
            port_ids = list(self.workflow.inputs.keys())
        elif step_id == special_id_for_outputs:
            port_ids = list(self.workflow.outputs.keys())
        elif step_id in self.workflow.steps:
            port_ids = list(self.workflow.steps[step_id].available_sources.keys())

        self.src_port.clear()
        self.src_port.addItems(port_ids)

        dst_node_ids = [_n for _n in [special_id_for_inputs] +
                        list(self.workflow.steps.keys()) +
                        [special_id_for_outputs] if _n != step_id]
        self.dst_node.clear()
        self.dst_node.addItems(dst_node_ids)

    @Slot()
    def dst_node_selected(self):
        step_id = self.dst_node.currentText()
        port_ids = []
        if step_id == special_id_for_inputs:
            port_ids = list(self.workflow.inputs.keys())
        elif step_id == special_id_for_outputs:
            port_ids = list(self.workflow.outputs.keys())
        elif step_id in self.workflow.steps:
            port_ids = list(self.workflow.steps[step_id].available_sources.keys())

        self.dst_port.clear()
        self.dst_port.addItems(port_ids)
