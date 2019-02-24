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

    def __init__(self):
        QWidget.__init__(self)

        self.command_line = QLineEdit()
        self.command_line.setToolTip("Enter commands here")
        self.command_line.returnPressed.connect(self.command_entered)

        self.command_log = QTextEdit()
        self.command_log.setReadOnly(True)
        self.command_log.setToolTip("Command and response history")

        layout = QVBoxLayout()
        layout.addWidget(self.command_line)
        layout.addWidget(self.command_log)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

    @Slot()
    def command_entered(self):
        cmd = self.command_line.text()
        response = "echo: {}".format(cmd)
        self.command_line.clear()
        self.response_received(cmd, response)

    @Slot(str, str)
    def response_received(self, command, response):
        self.command_log.moveCursor(QTextCursor.End)
        self.command_log.insertPlainText("\n" + "$> " + command + "\n")
        self.command_log.moveCursor(QTextCursor.End)
        self.command_log.insertPlainText(response)
        self.command_log.moveCursor(QTextCursor.End)
