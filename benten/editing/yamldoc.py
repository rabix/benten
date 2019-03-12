"""These are functions to generate edit operations on a YAML (Ydict) document."""
from typing import Tuple
from abc import ABC, abstractmethod
from enum import IntEnum

from ..implementationerror import ImplementationError
from .edit import EditMark, Edit
from .lineloader import parse_yaml_with_line_info, Ystr, Ydict, DocumentError


class LockedDueToYAMLErrors(Exception):
    pass


class UnableToCreateView(Exception):
    pass


class ContentsChanged(IntEnum):
    No = 0
    Yes = 1


class TextType(IntEnum):
    process = 1
    documentation = 2
    expression = 3


class BaseDoc(ABC):

    def __init__(self, raw_text):
        self.raw_text = raw_text
        self.raw_lines = raw_text.splitlines(keepends=True)

    def identical_to(self, raw_text: str):
        return self.raw_text == raw_text

    def set_raw_text(self, raw_text: str):
        if self.identical_to(raw_text):
            return ContentsChanged.No
        else:
            self.raw_text = raw_text
            self.raw_lines = raw_text.splitlines(keepends=True)
            return ContentsChanged.Yes

    @abstractmethod
    def set_raw_text_and_reparse(self, raw_text: str) -> ContentsChanged:
        pass


class PlainText(BaseDoc):

    def set_raw_text_and_reparse(self, raw_text: str) -> ContentsChanged:
        return self.set_raw_text(raw_text)


class YamlDoc(BaseDoc):
    def __init__(self, raw_text):
        super().__init__(raw_text)
        self.yaml = None
        self.last_good_yaml = None
        self.yaml_error = None

    def set_raw_text(self, raw_text: str):
        if super().set_raw_text(raw_text) == ContentsChanged.No:
            return ContentsChanged.No
        else:
            self.yaml = None
            self.yaml_error = None
            return ContentsChanged.Yes

    def set_raw_text_and_reparse(self, raw_text: str):
        if self.set_raw_text(raw_text) == ContentsChanged.No:
            return ContentsChanged.No
        else:
            self.parse_yaml()
            return ContentsChanged.yes

    def parse_yaml(self):
        if self.yaml is not None and self.yaml_error is None:
            return

        try:
            self.yaml = parse_yaml_with_line_info(self.raw_text, convert_to_lam=True) or Ydict.empty()
            self.yaml_error = None
            self.last_good_yaml = self.yaml
        except DocumentError as e:
            self.yaml_error = e

    def __contains__(self, path: Tuple[str]):
        sub_doc = self.yaml
        for p in path or []:
            if p in sub_doc:
                sub_doc = sub_doc[p]
            else:
                return False
        else:
            return True

    def __getitem__(self, path: Tuple[str]):
        sub_doc = self.yaml
        for p in path or []:
            sub_doc = sub_doc[p]
        return sub_doc

    @staticmethod
    def infer_section_type(path: Tuple[str]):
        if len(path) > 0:
            if path[-1] == "run":
                return TextType.process
            else:
                return TextType.documentation
        else:
            return TextType.documentation

    def get_raw_text_for_section(self, path: Tuple[str]):
        value = self.yaml[path]

        start_line, end_line = value.start.line, value.end.line
        sl = start_line
        indent_level = len(self.raw_lines[sl]) - len(self.raw_lines[sl].lstrip())

        if isinstance(value, Ydict):  # Currently, sole use case is in steps
            if value.flow_style:
                if value == {}:
                    return ""
                else:
                    raise UnableToCreateView("Flow style elements can not be edited in a view")
        elif isinstance(value, Ystr):  # Single line expressions and documentation
            # todo: check for expressions
            if value.style == "":
                return value

        lines_we_need = self.raw_lines[start_line:end_line]
        lines = [
            l[indent_level:] if len(l) > indent_level else "\n"
            for l in lines_we_need
        ]
        # All lines with text have the given indent level or more, so they are not an issue
        # Blank lines, however, can be zero length, hence the exception.
        return "".join(lines)

    def set_section_from_raw_text(self, raw_text, path: Tuple[str]) -> Edit:
        new_lines = self._apply_edit_to_lines(
            self._project_raw_text_to_section_as_edit(raw_text, path))
        diff_as_edit = YamlDoc.edit_from_quick_diff(self.raw_lines, new_lines)
        self.set_raw_text("".join(new_lines))
        return diff_as_edit

    # # We add this to an anchor so that we know what to add to a non-empty value
    # # This is required for when the original value was empty and expressed in flow
    # # style as an empty dict (e.g. steps) or an empty string (e.g. docs, expressions)
    # # and when they are substantial, we should pass the edit back with an appropriate
    # # preamble to carry out this transition
    # preamble = {
    #     TextType.process: "\n",
    #     TextType.documentation: "|-\n",
    #     TextType.expression: "|-\n"
    # }

    def _project_raw_text_to_section_as_edit(self, raw_text, path: Tuple[str]):
        original_value = self.yaml[path]
        if not raw_text.endswith("\n"):
            raw_text += "\n"
            # We need a newline between this segment and the next
            # Because we edit this as a block, the user can remove that last
            # newline, and we need to add it back to maintain the YAML structure
        raw_text_lines = raw_text.splitlines(keepends=True)
        projected_text_lines = []

        start = EditMark(original_value.start.line, original_value.start.column)
        end = EditMark(original_value.end.line, original_value.end.column)

        if raw_text == "\n":
            return Edit(start, end, raw_text, raw_text_lines)

        sl = original_value.start.line
        if len(self.raw_lines):
            indent_level = len(self.raw_lines[sl]) - len(self.raw_lines[sl].lstrip())
        else:
            indent_level = 0

        if isinstance(original_value, Ydict):  # Currently, sole use case is in steps
            if original_value.flow_style:
                if original_value == {}:
                    indent_level += 2
                    projected_text_lines += ["\n" + " " * indent_level]
                else:
                    raise ImplementationError("Should not be viewing flow style elements")
        elif isinstance(original_value, Ystr):  # Expressions and documentation
            if original_value.style == "" and "\n" in raw_text:
                indent_level += 2
                projected_text_lines += ["|-\n" + " " * indent_level]
            else:
                return Edit(start, end, raw_text, raw_text_lines)

        projected_text_lines += [((' '*indent_level) if len(l) > 1 and n > 0 else "") + l
                                 for n, l in enumerate(raw_text_lines)]
        # 1. First line should have no indent - the cursor position takes care of that
        # 2. All lines with text have the given indent level or more, so they are not an issue
        #    Blank lines, however, can be zero length, hence the exception.
        return Edit(start, end, None, projected_text_lines)

    def _apply_edit_to_lines(self, edit: Edit):
        existing_lines = self.raw_lines
        lines_to_insert = edit.text_lines

        if edit.end is None:
            edit.end = edit.start

        if edit.end.line != edit.start.line:
            edit.end.column = 0

        new_lines = existing_lines[:edit.start.line] + \
                    ([existing_lines[edit.start.line][:edit.start.column]] if edit.start.line < len(existing_lines) else []) + \
                    lines_to_insert + \
                    (([existing_lines[edit.end.line][edit.end.column:]] +
                      (existing_lines[edit.end.line + 1:] if edit.end.line + 1 < len(existing_lines) else []))
                     if edit.end.line < len(existing_lines) else [])

        return new_lines

    @staticmethod
    def edit_from_quick_diff(orig_lines, new_lines) -> Edit:
        L0 = len(orig_lines) - 1
        L1 = len(new_lines) - 1

        upper_n = L0
        for n in range(len(orig_lines)):
            if orig_lines[n] != new_lines[n]:
                upper_n = n
                break

        lower_n = 0
        for n in range(len(orig_lines)):
            if orig_lines[L0 - n] != new_lines[L1 - n]:
                lower_n = n
                break

        start = EditMark(upper_n, 0)
        end = EditMark(L0 - lower_n + 1, 0)

        return Edit(start, end, "".join(new_lines[upper_n:(L1 - lower_n + 1)]), [])
