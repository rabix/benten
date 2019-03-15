"""Mixin for ViewWidget that implements various commands that commandwidget will invoke"""
import pathlib

from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot, Signal

from ...editing.edit import Edit, EditMark


# Decorator that we use to add in information for the command, like help etc.
def cmeta(cmd, cmd_help, syn=None):
    def wrap(func):
        func.is_command = True
        func.cmd = cmd
        func.help = cmd_help
        func.syn = syn or []
        return func
    return wrap


def onlyclt(func):
    def cmd(self, args):
        if self.process_type() == "CommandLineTool":
            return func(self, args)
        else:
            return "Can only do this on CommandLineTool"
    return cmd


def onlywf(func):
    def cmd(self, args):
        if self.process_type() == "Workflow":
            return func(self, args)
        else:
            return "Can only do this on Workflow"
    return cmd


class ViewWidgetCommands:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_window.set_up_dispatcher(self)
        # We call this now that we are in the list of mixins
        # Note that we should come before ViewWidgetBase whose constructor
        # is invoked before us, because of chained calls to super and whose
        # features we might be using

    @cmeta(
        cmd="create",
        cmd_help="create <clt|et|wf> : When in an empty document, create a scaffold"
                 " for CommandLineTool, ExpressionTool or Workflow")
    def create_scaffold(self, args):
        blk = QSignalBlocker(self.code_editor)

        if self.cwl_doc.raw_cwl:
            return "Document not empty, will not create scaffold"

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
            self.code_editor.insert_text(edit)
            self.programmatic_edit()
            return "Added scaffold from file {}".format(scaffold_path)
        else:
            return "No scaffold for process type {}. Valid arguments are {}".format(arg, list(choices.keys()))



#
#
# class CommandWidget(QWidget):
#
#     def __init__(self, parent):
#         QWidget.__init__(self)
#
#         # This gives us the global context to access any functionality we need to
#         # get stuff done
#         self.bw: 'BentenWindow' = parent
#
#         self.command_line = QLineEdit()
#         self.command_line.setFont(QFont("Menlo,11,-1,5,50,0,0,0,0,0,Regular"))
#         self.command_line.setToolTip("Enter commands here")
#         self.command_line.returnPressed.connect(self.command_entered)
#
#         self.command_log = QTextEdit()
#         self.command_log.setReadOnly(True)
#         self.command_log.setFont(QFont("Menlo,11,-1,5,50,0,0,0,0,0,Regular"))
#
#         self.command_log.setToolTip("Command and response history")
#
#         layout = QVBoxLayout()
#         layout.addWidget(self.command_line)
#         layout.addWidget(self.command_log)
#         layout.setMargin(0)
#         layout.setSpacing(0)
#         self.setLayout(layout)
#
#         self.dispatch_table, self.help_table = self._set_up_dispatcher()
#
#     def _set_up_dispatcher(self):
#         table = {
#             "help": {
#                 "synonyms": ["?", "h"],
#                 "help": "Print help",
#                 "call": self.print_help
#             },
#             "create": {
#                 "help": "create <clt|et|wf> : When in an empty document, create a scaffold for CommandLineTool, "
#                         "ExpressionTool or Workflow",
#                 "call": self.bw.create_scaffold
#             },
#             "docker": {
#                 "help": "docker <docker_image> : Add DockerRequirement to CLT",
#                 "call": self.bw.scaffold_docker
#             },
#             "new": {
#                 "help": "new <step_id> [path] : Create scaffold for new inline step, or, "
#                         "if path is given new linked step",
#                 "call": self.bw.scaffold_new_step
#             },
#             "goto": {
#                 "synonyms": ["g"],
#                 "help": "goto <stepid> : Goto step",
#                 "call": self.goto_step
#             },
#             "list": {
#                 "synonyms": ["l"],
#                 "help": "list : List all steps in workflow",
#                 "call": self.list_steps
#             },
#             "open": {
#                 "synonyms": ["o"],
#                 "help": "open <step_id> [step_id, ...] : Open step(s) in new tab(s)",
#                 "call": self.bw.step_ids_to_open
#             },
#             "revisions": {
#                 "help": "Print list of available revisions",
#                 "call": self.get_app_revisions
#             }
#         }
#
#         expanded_table = {}
#         for k, v in table.items():
#             for _k in [k] + v.get("synonyms", []):
#                 expanded_table[_k] = v
#
#         return expanded_table, table
#
#     @Slot()
#     def command_entered(self):
#         cmd_line = self.command_line.text()
#         cmd, *arguments = cmd_line.split()
#
#         if cmd in self.dispatch_table:
#             try:
#                 response = str(self.dispatch_table[cmd]["call"](arguments))
#             except Exception as e:
#                 response = f"Command error:\n{e}"
#         else:
#             response = "Unknown command: {}".format(cmd)
#
#         self.command_line.clear()
#         self.response_received(cmd, arguments, response)
#
#     @Slot(str, str)
#     def response_received(self, command, arguments, response):
#         self.command_log.moveCursor(QTextCursor.End)
#         self.command_log.insertPlainText("\n" + "$> " + command + " " + " ".join(arguments) + "\n")
#         self.command_log.moveCursor(QTextCursor.End)
#         self.command_log.insertPlainText(response)
#         self.command_log.moveCursor(QTextCursor.End)
#
#     def print_help(self, args):
#         return "\n".join("{}\t - {}".format(", ".join([k] + v.get("synonyms", [])), v["help"])
#                          for k, v in self.help_table.items())
#
#     def list_steps(self, args):
#         if self.bw.cwl_doc.process_type() in ["CommandLineTool", "ExpressionTool"]:
#             return "This process type does not contain steps"
#
#         return "Steps:\n" + "\t\n".join(step for step in self.bw.cwl_doc.cwl_dict["steps"].keys())
#
#     def goto_step(self, args):
#         if self.bw.cwl_doc.process_type() in ["CommandLineTool", "ExpressionTool"]:
#             return "This process type does not contain steps"
#
#         return self.bw.highlight_step(args[0], focus_conn=False)
#
#     def get_app_revisions(self, args):
#         return "\n".join(
#             "v{}: {} - {}".format(rev["sbg:revision"], rev["sbg:revisionNotes"], rev["sbg:modifiedBy"])
#             for rev in self.bw.cwl_doc.get_app_revisions())
