"""The QT Wrapper around the ace editor using QWebEngineView.
See: https://kaushikghose.wordpress.com/2019/03/18/embed-ace-editor-in-a-python-qt-app/

Because of the asynchronous nature of our communication with Ace some things are different.
For example, in the earlier design we would perform some operation on the rest of the IDE,
like switch a tab, and we would just ask for the code in the editor in order to refresh the
model.

With this doubly-asynchronous set up we have to do the following: When we switch tabs we
*ask* the editor for the latest code and then wait until the editor supplies us with the
code, *then* we do an update, based on that.

Similarly, for manual edits we wait until the editor sends a signal with the latest text,
we then do an update based on that. For this reason we are free to move the edit throttler
into this class.

If we ever want to move back from the Ace editor to a built in QT component, like a QPlainTextEdit,
we should wrap it in this kind of interface for ease of use - but I doubt we'll go back.
"""
from typing import List

from PySide2.QtCore import QObject, QUrl, QTimer, QJsonValue, QJsonArray, Signal, Slot
from PySide2.QtWidgets import QApplication
from PySide2.QtWebChannel import QWebChannel
from PySide2.QtWebEngineWidgets import QWebEngineView

from ...configuration import Configuration
from ...editing.edit import Edit
from ...editing.documentproblem import DocumentProblem

from .editoripc import EditorIPC

import benten.gui.ace.resources


import logging
logger = logging.getLogger(__name__)


class Editor(QWebEngineView):

    new_text_available = Signal(str)

    def __init__(self, *args, config: Configuration, **kwargs):
        super().__init__(*args, **kwargs)

        self.config = config

        self.ipc = EditorIPC(config)

        self.cached_text = None
        self.ipc.text_ready.connect(self.text_ready)

        # The channel object has to persist. Doing registerObject does not keep a reference apparently
        page = self.page()
        channel = QWebChannel(page)
        channel.registerObject("ipc", self.ipc)
        page.setWebChannel(channel)
        page.load(QUrl("qrc:/index.html"))

    def set_text(self, raw_text):
        if self.cached_text == raw_text:
            logger.debug("New text unchanged. Ignoring")
            return

        self.ipc.wait()
        self.ipc.send_text_js_side.emit(raw_text)
        self.cached_text = raw_text
        logger.debug("New text sent to editor")

    def insert_text(self, edit: Edit):
        if edit.end is None:
            edit.end = edit.start

        self.ipc.apply_edit.emit(edit.start.line, edit.start.column,
                                 edit.end.line, edit.end.column,
                                 edit.text)

    @Slot(str)
    def text_ready(self, text):
        self.cached_text = text
        self.new_text_available.emit(text)

    def scroll_to(self, line):
        self.ipc.scroll_to.emit(line)

    def mark_errors(self, problems: List[DocumentProblem]):
        for problem in problems:
            self.ipc.send_error_annotation(
                problem.line, problem.column, problem.message, problem.problem_type.name)
