from PySide2.QtCore import QObject, QJsonValue, Signal, Slot
from PySide2.QtWidgets import QApplication

from .manualeditthrottler import ManualEditThrottler

import logging
logger = logging.getLogger(__name__)


class EditorIPC(QObject):

    set_option = Signal(str, str)
    fetch_text = Signal()
    send_text_js_side = Signal(str)
    apply_edit = Signal(int, int, int, int, str)
    scroll_to = Signal(int)
    send_error_annotation = Signal(int, int, str, str)
    send_auto_completions = Signal('QVariantList')

    text_ready = Signal(str)

    def __init__(self, editor, parent=None):
        super().__init__(parent)
        self.editor = editor

        self._setup_complete = False

        self.manual_edit_throttler = ManualEditThrottler(self.editor.config.getfloat("editor", "type_burst_window"))
        self.manual_edit_throttler.timer.timeout.connect(lambda x=None: self.fetch_text.emit())

    def wait(self):
        while not self._setup_complete:
            QApplication.processEvents()

    @Slot()
    def editor_ready(self):
        self._setup_complete = True
        logger.debug("ACE editor ready")

    # Any function that should be callable from JS, has to be declared a slot

    @Slot()
    def fetch_options(self):
        for k, v in self.editor.config.items("ace-options"):
            logger.debug("ACE editor: Set {} to {}".format(k, v))
            self.set_option.emit(k, v)

    @Slot()
    def user_typing(self):
        self.manual_edit_throttler.restart_edit_clock()

    @Slot(str)
    def send_text_python_side(self, raw_text):
        self.editor.new_text_available.emit(raw_text)
        # self.text_ready.emit(raw_text)

    @Slot(QJsonValue, str)
    def get_auto_complete_options(self, pos, prefix):
        print(pos.toVariant(), prefix)
        if self.editor.document_model is not None:
            self.send_auto_completions.emit(
                self.editor.document_model.get_auto_completions(pos, prefix))