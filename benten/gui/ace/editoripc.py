import yaml
import pathlib

from PySide2.QtCore import QObject, QJsonValue, Signal, Slot
from PySide2.QtWidgets import QApplication

from .manualeditthrottler import ManualEditThrottler

import logging
logger = logging.getLogger(__name__)


class EditorIPC(QObject):

    set_option = Signal(str, str)
    set_snippets = Signal('QVariantList')

    fetch_text = Signal()
    send_text_js_side = Signal(str)
    apply_edit = Signal(int, int, int, int, str)
    scroll_to = Signal(int)
    send_error_annotations = Signal('QVariantList')
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
    def fetch_settings(self):
        snippet_file = self.editor.config._resolve_path(pathlib.Path("snippets.yaml"))
        if snippet_file.exists():
            self.set_snippets.emit(yaml.load(snippet_file.open("r").read()))

        for k, v in self.editor.config.items("ace-options"):
            logger.debug("ACE editor: Set {} to {}".format(k, v))
            self.set_option.emit(k, v)

    @Slot()
    def user_typing(self):
        self.manual_edit_throttler.restart_edit_clock()

    @Slot(str)
    def send_text_python_side(self, raw_text):
        if self.editor.cached_text != raw_text:
            self.editor.cached_text = raw_text
            self.editor.new_text_available.emit(raw_text)
            logger.debug("Received changed text from ACE")
        else:
            logger.debug("Received text from ACE is unchanged")

    @Slot(QJsonValue, str)
    def get_auto_complete_options(self, pos, prefix):
        # TODO: a cheap autocompleter with heuristics that doesn't need to parse the whole document to make suggestions
        return [
            {
                "caption": "example",
                "name": "Example",
                "value": "value" + prefix,
                "snippet": "My my\nwhat a beautiful sky",
                "score": 10,
                "meta": "Metadata"
            }
        ]
        # _pos = pos.toVariant()
        # print(_pos, prefix)
        #
        # # XXXXX
        # from ...editing.yamlview import YamlView
        # from ...models.commandlinetool import CommandLineTool
        # self.editor.document_model = CommandLineTool(YamlView(raw_text=self.editor.cached_text))
        # if self.editor.document_model is not None:
        #     self.send_auto_completions.emit(
        #         self.editor.document_model.get_auto_completions(
        #             line=int(_pos["row"]), column=int(_pos["column"]), prefix=prefix))
