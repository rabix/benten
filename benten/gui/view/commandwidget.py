"""This handles the command line bar and the response log.
It consists of a single-line text edit on top. You enter commands into this box.
Below it is a read only multiline text box that shows the response to the commands.
The command is echoed and the response printed below.
"""
import pathlib

from PySide2.QtCore import Slot, Signal
from PySide2.QtWidgets import QVBoxLayout, QLineEdit, QTextEdit, QWidget
from PySide2.QtGui import QTextCursor
from PySide2.QtGui import QFontDatabase

from ...editing.edit import Edit, EditMark
from ...editing.yamlview import YamlView

from ..ace.editor import Editor

import logging

logger = logging.getLogger(__name__)


# Decorator that we use to add in information for the command, like help etc.
def meta(cmd, cmd_help, syn=None):
    def wrap(func):
        func.is_command = True
        func.cmd = cmd
        func.help = cmd_help
        func.syn = syn or []
        return func
    return wrap


def only_clt(func):
    def cmd(self, args):
        if self.process_type() == "CommandLineTool":
            return func(self, args)
        else:
            return "Can only do this on CommandLineTool: This is {}".format(self.process_type())
    return cmd


def only_wf(func):
    def cmd(self, args):
        if self.process_type() == "Workflow":
            return func(self, args)
        else:
            return "Can only do this on Workflow"
    return cmd


class CommandWidget(QWidget):

    proposed_edit = Signal(object)
    step_selected = Signal(str)

    def __init__(self, editor: Editor, parent=None):
        QWidget.__init__(self, parent=parent)

        self.editor = editor
        # We need a reference to the editor since several commands operate on the raw text both
        # reading and writing back to the original document

        self.command_line = QLineEdit()
        self.command_line.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
        self.command_line.setToolTip("Enter commands here")
        self.command_line.returnPressed.connect(self.command_entered)

        self.command_log = QTextEdit()
        self.command_log.setReadOnly(True)
        self.command_line.setFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))

        self.command_log.setToolTip("Command and response history")

        layout = QVBoxLayout()
        layout.addWidget(self.command_line)
        layout.addWidget(self.command_log)
        layout.setMargin(0)
        layout.setSpacing(0)
        self.setLayout(layout)

        self.dispatch_table, self.help_table = self.set_up_dispatcher()

    def set_up_dispatcher(self):
        table = {
            "help": {
                "synonyms": ["?", "h"],
                "help": "help: Print help",
                "call": self.print_help
            }
        }

        for func_name in sorted(self.__dir__()):
            fn = getattr(self, func_name)
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

        return expanded_table, table

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
        return "\n".join("{}\n{}".format(
            v["help"], "Synonyms: {}\n".format(v.get("synonyms")) if v.get("synonyms") else "")
                         for k, v in self.help_table.items())

    #
    # All the built-in commands
    #

    @meta(
        cmd="sbpush",
        cmd_help="sbpush <message> [project/id] : Push this app to the platform")
    def sbpush(self, args):

        cwl_view = YamlView(raw_text=self.editor.cached_text)
        if cwl_view.yaml is None:
            message = "Can not push malformed CWL document"
            logger.debug(message)
            raise RuntimeError(message)

        app_path = args[0] if len(args) else None

        from ...sbg.push import push

        app = push(api, cwl_view.yaml, app_path)


        arg = args[0] if isinstance(args, list) else args

        choices = {
            "clt": "command-line-tool.cwl",
            "et": "expression-tool.cwl",
            "wf": "workflow.cwl"
        }
        scaffold_path = pathlib.Path(
            self.config.getpath("cwl", "template_dir"), choices.get(arg, "doesnotexist"))

        if scaffold_path.exists():
            edit = Edit(start=EditMark(line=0, column=0), end=None,
                        text=scaffold_path.open("r").read(), text_lines=[])

            self.proposed_edit.emit(edit)
            return "Added scaffold from file {}".format(scaffold_path)
        else:
            return "No scaffold for process type {}. Valid arguments are {}".format(arg, list(choices.keys()))

    @meta(
        cmd="docker",
        cmd_help="docker <docker_image> : Add DockerRequirement to CLT")
    @only_clt
    def docker_scaffold(self, args):
        if len(args) != 1:
            return "Incorrect number of arguments"

        docker_image = args[0]
        edit = self.attached_view.doc.insert_into_lom(
            path=("requirements",),
            key="DockerRequirement",
            key_field="class",
            entry="dockerPull: {}\n".format(docker_image)
        )

        self.proposed_edit.emit(edit)
        return "Added DockerRequirement"

    @meta(
        cmd="add",
        cmd_help="add <step_id> [path] : Create scaffold for new inline step, "
                 "or, if path is given new linked step.")
    @only_wf
    def add_step_scaffold(self, args):
        if not 0 < len(args) < 3:
            return "Arguments are <step_id> [path]"

        step_id = args[0]
        path = pathlib.Path(args[1]) if len(args) > 1 else None

        scaffold_path = pathlib.Path(
            self.config.getpath("cwl", "template_dir"), "step-template.cwl")

        if not scaffold_path.exists():
            return "Couldn't find step scaffold file {}".format(scaffold_path)

        scaffold = scaffold_path.open("r").read()
        rel_path = self.attached_view.get_root().get_rel_path(path) if path else None

        edit = self.process_model.add_step(
            step_scaffold=scaffold, rel_path=rel_path, path=path, step_id=step_id)

        self.proposed_edit.emit(edit)
        return "Added step"




    # def list_steps(self, args):
    #     if self.bw.cwl_doc.process_type() in ["CommandLineTool", "ExpressionTool"]:
    #         return "This process type does not contain steps"
    #
    #     return "Steps:\n" + "\t\n".join(step for step in self.bw.cwl_doc.cwl_dict["steps"].keys())
    #
    # def goto_step(self, args):
    #     if self.bw.cwl_doc.process_type() in ["CommandLineTool", "ExpressionTool"]:
    #         return "This process type does not contain steps"
    #
    #     return self.bw.highlight_step(args[0], focus_conn=False)
    #
    # def get_app_revisions(self, args):
    #     return "\n".join(
    #         "v{}: {} - {}".format(rev["sbg:revision"], rev["sbg:revisionNotes"], rev["sbg:modifiedBy"])
    #         for rev in self.bw.cwl_doc.get_app_revisions())
