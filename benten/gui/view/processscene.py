import pathlib

from PySide2.QtWidgets import QGraphicsScene, QGraphicsSceneDragDropEvent, QGraphicsSceneMouseEvent
from PySide2.QtCore import Qt, Signal, Slot


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
    double_click = Signal(QGraphicsSceneMouseEvent)

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

        self.nodes_added(wf_list)

    def mouseDoubleClickEvent(self, event:QGraphicsSceneMouseEvent):
        self.double_click.emit(event)

    #
    # @Slot(int, int)
    # def connection_clicked(self, row, col):
    #     conn = self.conn_table.item(row, col).data(Qt.UserRole)
    #     logger.debug("Scroll to line {}".format(conn.line[0]))
    #     self.code_editor.scroll_to(conn.line[0])
    #
    #
    # def step_ids_to_open(self, step_ids):
    #     steps = [step for step in self.process_model.steps.values() if step.id in step_ids ]
    #     self.open_steps.emit((self.attached_view, steps))
    #
    # @Slot(list)
    # def nodes_added(self, cwl_path_list):
    #     blk = QSignalBlocker(self.code_editor)
    #     for p in cwl_path_list:
    #         self.update_process_model_from_code()
    #         self.code_editor.insert_text(self.process_model.add_step(p))
    #     self.programmatic_edit()
