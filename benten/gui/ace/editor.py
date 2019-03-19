"""The QT Wrapper around the ace editor using QWebEngineView.
See: https://kaushikghose.wordpress.com/2019/03/18/embed-ace-editor-in-a-python-qt-app/"""
import sys
from PySide2.QtCore import QObject, QUrl, Signal, Slot
from PySide2.QtWidgets import QApplication
from PySide2.QtWebChannel import QWebChannel
from PySide2.QtWebEngineWidgets import QWebEngineView

from benten.configuration import Configuration
import benten.gui.ace.resources

html = """
<!DOCTYPE html>
<html lang="en">
<head>
<title>Benten</title>

<script src="qrc:/qtwebchannel/qwebchannel.js" type="text/javascript"></script>
// This file comes bundled with Pyside2 and the resource bundler knows to include it ...
<script src="qrc:/ace-builds/src-min-noconflict/ace.js" type="text/javascript" charset="utf-8"></script>

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

    // This stuff we insist upon
    editor.setOptions({
        useSoftTabs: true,
        navigateWithinSoftTabs: false,  // hmm, could cause confusion ...
        tabSize: 2
    });           
    
    editor.setTheme("ace/theme/twilight");
    // editor.session.setMode("ace/mode/cwl");


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

        ipc.set_option.connect(function (option, value) {
            editor.setOption(option, value) 
        })

        ipc.fetch_options()

        // An example of receiving information pushed from the Python side
        // It's really neat how this looks just like the Python code
        ipc.send_text_js_side.connect(function(text) {
            editor.session.setValue(text)
        })

        // An example of sending information to the Python side
        editor.session.on('change', function(delta) {
            ipc.send_text_python_side(editor.getValue(), function(val) {} );
            // Python functions return a value, even if it is None. So we need to pass a
            // dummy callback function to handle the return
        })

        ipc.send_error_annotation.connect(set_error_annotation);

    });

});
</script>

</head>
<body>

<div id="editor">Seven Bridges Rabix Benten</div>

</body>
</html>
"""


class EditorIPC(QObject):

    set_option = Signal(str, str)
    send_text_js_side = Signal(str)
    apply_edit = Signal(int, int, int, int, str)
    send_error_annotation = Signal(int, int, str, str)

    def __init__(self, config: Configuration, parent=None):
        super().__init__(parent)
        self.config = config
        self.editor_options = "Hello!"

    # Any function that should be callable from JS, has to be declared a slot
    @Slot()
    def fetch_options(self):
        print({k:v for k, v in self.config.items("editor")})
        for k, v in self.config.items("editor"):
            self.set_option.emit(k, v)
        # return {k:v for k, v in }
        return "Hello!"

    @Slot(str)
    def send_text_python_side(self, message):
        print(message)


class Editor(QWebEngineView):

    textChanged = Signal()

    def __init__(self, *args, config: Configuration, **kwargs):
        super().__init__(*args, **kwargs)

        page = self.page()

        self.ipc = EditorIPC(config)
        # The channel object has to persist. Doing registerObject does not keep a reference apparently
        channel = QWebChannel(page)
        channel.registerObject("ipc", self.ipc)

        page.setWebChannel(channel)
        page.setHtml(html, QUrl("qrc:/index.html"))

    def set_text(self, str):
        return None


if __name__ == '__main__':

    app = QApplication(sys.argv)

    view = Editor(config={})
    view.show()

    app.exec_()
