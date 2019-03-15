"""This handles the command line bar and the response log.
It consists of a single-line text edit on top. You enter commands into this box.
Below it is a read only multiline text box that shows the response to the commands.
The command is echoed and the response printed below. The latest command is on top.
"""
from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot, Signal
from PySide2.QtWidgets import QVBoxLayout, QLineEdit, QTextEdit, QTableWidgetItem, QWidget, \
    QAbstractItemView, QGraphicsSceneMouseEvent, QTabWidget, QAction, QFontDialog, QCompleter
from PySide2.QtGui import QTextCursor, QFont

import logging

logger = logging.getLogger(__name__)


class CommandWidget(QWidget):

    def __init__(self, parent):
        QWidget.__init__(self, parent=parent)

        # # This gives us the global context to access any functionality we need to
        # # get stuff done
        # self.bw: 'BentenWindow' = parent

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

        self.dispatch_table, self.help_table = None, None

    def set_up_dispatcher(self, _parent):
        table = {
            "help": {
                "synonyms": ["?", "h"],
                "help": "Print help",
                "call": self.print_help
            }
        }

        for fname in _parent.__dir__():
            fn = getattr(_parent, fname)
            if hasattr(fn, "is_command"):
                logger.debug("Installed command  '{}'".format(fn.cmd))
                table[fn.cmd] = {
                    "synonyms": fn.syn,
                    "help": fn.help,
                    "call": fn
                }

        expanded_table = {}
        for k, v in table.items():
            for _k in [k] + v.get("synonyms", []):
                expanded_table[_k] = v

        self.dispatch_table, self.help_table = expanded_table, table

    @Slot()
    def command_entered(self):
        cmd_line = self.command_line.text()
        cmd, *arguments = cmd_line.split()

        if cmd in self.dispatch_table:
            try:
                response = str(self.dispatch_table[cmd]["call"](arguments))
            except Exception as e:
                response = f"Command error:\n{e}"
        else:
            response = "Unknown command: {}".format(cmd)

        self.command_line.clear()
        self.response_received(cmd, arguments, response)

    @Slot(str, str)
    def response_received(self, command, arguments, response):
        self.command_log.moveCursor(QTextCursor.End)
        self.command_log.insertPlainText("\n" + "$> " + command + " " + " ".join(arguments) + "\n")
        self.command_log.moveCursor(QTextCursor.End)
        self.command_log.insertPlainText(response)
        self.command_log.moveCursor(QTextCursor.End)

    def print_help(self, args):
        return "\n".join("{}\t - {}".format(", ".join([k] + v.get("synonyms", [])), v["help"])
                         for k, v in self.help_table.items())

    def list_steps(self, args):
        if self.bw.cwl_doc.process_type() in ["CommandLineTool", "ExpressionTool"]:
            return "This process type does not contain steps"

        return "Steps:\n" + "\t\n".join(step for step in self.bw.cwl_doc.cwl_dict["steps"].keys())

    def goto_step(self, args):
        if self.bw.cwl_doc.process_type() in ["CommandLineTool", "ExpressionTool"]:
            return "This process type does not contain steps"

        return self.bw.highlight_step(args[0], focus_conn=False)

    def get_app_revisions(self, args):
        return "\n".join(
            "v{}: {} - {}".format(rev["sbg:revision"], rev["sbg:revisionNotes"], rev["sbg:modifiedBy"])
            for rev in self.bw.cwl_doc.get_app_revisions())
