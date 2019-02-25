"""This handles the command line bar and the response log.
It consists of a single-line text edit on top. You enter commands into this box.
Below it is a read only multiline text box that shows the response to the commands.
The command is echoed and the response printed below. The latest command is on top.
"""
from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot, Signal
from PySide2.QtWidgets import QVBoxLayout, QLineEdit, QTextEdit, QTableWidgetItem, QWidget, \
    QAbstractItemView, QGraphicsSceneMouseEvent, QTabWidget, QAction, QFontDialog
from PySide2.QtGui import QTextCursor, QPainter, QFont


class CommandWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self)

        self.bw: 'BentenWindow' = parent

        self.command_line = QLineEdit()
        self.command_line.setFont(QFont("Menlo,11,-1,5,50,0,0,0,0,0,Regular"))
        self.command_line.setToolTip("Enter commands here")
        self.command_line.returnPressed.connect(self.command_entered)

        self.command_log = QTextEdit()
        self.command_log.setReadOnly(True)
        self.command_log.setFont(QFont("Menlo,11,-1,5,50,0,0,0,0,0,Regular"))

        self.command_log.setToolTip("Command and response history")

        layout = QVBoxLayout()
        layout.addWidget(self.command_line)
        layout.addWidget(self.command_log)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.dispatch_table = self._set_up_dispatcher()

    def _set_up_dispatcher(self):
        return {
            "help": (self.print_help, "Print help"),
            "?": (self.print_help, "Print help"),
            "revisions": (self.get_app_revisions, "Print list of available revisions")
        }

    @Slot()
    def command_entered(self):
        cmd_line = self.command_line.text()
        cmd, *arguments = cmd_line.split()

        if cmd in self.dispatch_table:
            try:
                response = str(self.dispatch_table[cmd][0](arguments))
            except Exception as e:
                response = f"Command error:\n{e}"
        else:
            response = "Unknown command: {}".format(cmd)

        self.command_line.clear()
        self.response_received(cmd, response)

    @Slot(str, str)
    def response_received(self, command, response):
        self.command_log.moveCursor(QTextCursor.End)
        self.command_log.insertPlainText("\n" + "$> " + command + "\n")
        self.command_log.moveCursor(QTextCursor.End)
        self.command_log.insertPlainText(response)
        self.command_log.moveCursor(QTextCursor.End)

    def print_help(self, *args):
        return "\n".join("{}\t - {}".format(k, v[1]) for k, v in self.dispatch_table.items())

    def get_app_revisions(self, *args):
        return "\n".join(
            "v{}: {} - {}".format(rev["sbg:revision"], rev["sbg:revisionNotes"], rev["sbg:modifiedBy"])
            for rev in self.bw.cwl_doc.get_app_revisions())
