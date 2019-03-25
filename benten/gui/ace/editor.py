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

import benten.gui.ace.resources


import logging
logger = logging.getLogger(__name__)


html = """
<!DOCTYPE html>
<html lang="en">
<head>
<title>Benten</title>

<script src="qrc:/qtwebchannel/qwebchannel.js" type="text/javascript"></script>
// This file comes bundled with Pyside2 and the resource bundler knows to include it ...
<script src="qrc:/ace-builds/src-min-noconflict/ace.js" type="text/javascript" charset="utf-8"></script>
<script src="qrc:/ace-builds/src-min-noconflict/ext-language_tools.js" type="text/javascript"></script>
<script src="qrc:/cwl_snippets.js" type="text/javascript"></script>

<style type="text/css" media="screen">
    #editor {
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
    }
</style>

<script>
document.addEventListener("DOMContentLoaded", function () {
    // It is safest to set up this apparatus after the page has finished loading

    'use strict';

    var placeholder = document.getElementById('editor');

    var editor = ace.edit("editor");

    var snippetManager = ace.require("ace/snippets").snippetManager
    snippetManager.register(cwl_snippets, "yaml");
        
    editor.session.setMode("ace/mode/yaml");
    editor.setAnimatedScroll(true)

    // https://stackoverflow.com/a/42122466/2512851
    var set_error_annotation = function(row, column, err_msg, type) {
        editor.getSession().setAnnotations([{
            row: row,
            column: column,
            text: err_msg, // Or the Json reply from the parser
            type: type // error, warning, and information
        }]);
    }

    new QWebChannel(qt.webChannelTransport, function(channel) {
        // All the functions we use to communicate with the Python code are here
       
        var ipc = channel.objects.ipc
        
        ipc.fetch_text.connect( function() {
            ipc.send_text_python_side(editor.getValue(), function(val) {} );
            // Python functions return a value, even if it is None. So we need to pass a
            // dummy callback function to handle the return
        })

        ipc.send_text_js_side.connect(function(text) {
            editor.session.setValue(text)
        })

        ipc.apply_edit.connect( function(l0, c0, l1, c1, text) {
            var range = new Range(l0, c0, l1, c1)
            editor.addSelectionMarker(range)
            editor.insert(text)
        })

        editor.session.on('change', function(delta) {
            ipc.user_typing()
        })

        ipc.scroll_to.connect( function(line) {
            editor.scrollToLine(line, true)
            editor.moveCursorTo(line, 0)
        })
        ipc.send_error_annotation.connect(set_error_annotation);

        // I do wish there was a way to retrieve a value from the 
        ipc.set_option.connect(function (option, value) {
            editor.setOption(option, value) 
        })
        ipc.fetch_options()

        // Python based, context/syntax aware completer
        let langTools = ace.require('ace/ext/language_tools');
        var customCompleter = {
            getCompletions: function(editor, session, pos, prefix, callback) {
                ipc.send_auto_completions.connect(function(compl) {
                    callback(null, compl)
                })                
                ipc.get_auto_complete_options(pos, prefix)
            }
        }
        langTools.addCompleter(customCompleter);        
        
        // This stuff we insist upon regardless of what the user sets
        editor.setOptions({
            useSoftTabs: true,
            navigateWithinSoftTabs: false,  // hmm, could cause confusion ...
            tabSize: 2,
            enableBasicAutocompletion: true,
            enableSnippets: true,
            enableLiveAutocompletion: true            
        });        

        ipc.editor_ready()
    });

});
</script>

</head>
<body>

<div id="editor">Seven Bridges Rabix Benten</div>

</body>
</html>
"""


class ManualEditThrottler:
    """Each manual edit we do (letter we type) triggers a manual edit. We need to manage
    these calls so they don't overwhelm the system and yet not miss out on the final edit in
    a burst of edits. This manager handles that job effectively."""

    def __init__(self, burst_window):
        self.burst_window = burst_window
        # We allow upto a <burst_window> pause in typing before parsing the edit
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.setInterval(int(self.burst_window * 1000))
        logger.debug("Burst window set to {}s".format(self.burst_window))

    def restart_edit_clock(self):
        logger.debug("User still typing ...")
        self.timer.start()

    def flush(self):
        if self.timer.isActive():
            self.timer.stop()
            self.timer.timeout.emit()


class EditorIPC(QObject):

    set_option = Signal(str, str)
    fetch_text = Signal()
    send_text_js_side = Signal(str)
    apply_edit = Signal(int, int, int, int, str)
    scroll_to = Signal(int)
    send_error_annotation = Signal(int, int, str, str)
    send_auto_completions = Signal('QVariantList')

    text_ready = Signal(str)

    def __init__(self, config: Configuration, parent=None):
        super().__init__(parent)
        self.config = config

        self._setup_complete = False

        self.manual_edit_throttler = ManualEditThrottler(self.config.getfloat("editor", "type_burst_window"))
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
        for k, v in self.config.items("ace-options"):
            logger.debug("ACE editor: Set {} to {}".format(k, v))
            self.set_option.emit(k, v)

    @Slot()
    def user_typing(self):
        self.manual_edit_throttler.restart_edit_clock()

    @Slot(str)
    def send_text_python_side(self, raw_text):
        self.text_ready.emit(raw_text)

    @Slot(QJsonValue, str)
    def get_auto_complete_options(self, pos, prefix):
        print(pos.toVariant(), prefix)
        self.send_auto_completions.emit([
            {
                "caption": "example",
                "name": "Example",
                "value": "value" + prefix,
                "snippet": "My my\nwhat a beautiful sky",
                "score": 10,
                "meta": "Metadata"
            }
        ])


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
        page.setHtml(html, QUrl("qrc:/index.html"))

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
