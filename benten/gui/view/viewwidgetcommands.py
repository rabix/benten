"""Mixin for ViewWidget that implements various commands that commandwidget will invoke"""
import pathlib

from PySide2.QtCore import Qt, QSignalBlocker, QTimer, Slot, Signal

from ...editing.edit import Edit, EditMark


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


class ViewWidgetCommands:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.command_window.set_up_dispatcher(self)
        # We call this now that we are in the list of mixins
        # Note that we should come before ViewWidgetBase whose constructor
        # is invoked before us, because of chained calls to super and whose
        # features we might be using

    def process_type(self):
        return self.attached_view.doc.yaml.get("class", "unknown")

    @meta(
        cmd="create",
        cmd_help="create <clt|et|wf> : When in an empty document, create a scaffold"
                 " for CommandLineTool, ExpressionTool or Workflow")
    def create_scaffold(self, args):

        if self.get_text():
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
            blk = QSignalBlocker(self.code_editor)
            self.apply_edit(edit)
            self.programmatic_edit()
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

        blk = QSignalBlocker(self.code_editor)
        self.apply_edit(edit)
        self.programmatic_edit()
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
        blk = QSignalBlocker(self.code_editor)
        self.apply_edit(edit)
        self.programmatic_edit()
        return "Added step"

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
