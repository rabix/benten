"""This abstracts out a framework for keeping track of views and computing the backward and
forward edit projections from the view. For now we just handle block elements.

It's main responsibility is to make sure edits are synchronized across different
views of a document. As such we do not implement process type specific logic here, but make
it somewhat general.

There are two types of fragments
    - those that can be sub-viewed further and
    - those that can not.

It has some special rules that are a compromise between maintaining hand edited text and
ease of use

1. We refuse to create and apply edits from a subview of a flow style dictionary unless the
   dictionary is empty. In such a case an edit returning a non-empty dictionary results in
   block style in the original. This allows us to insert empty steps in a workflow and then
   open them in a subview for editing


When using a view, here are some guidelines:

Q. What happens if we have a YAML error in any one of the linked views?
A. We should lock the user to that view until the error is fixed

Q. What happens if we delete a child from a parent?
A. The child view is set to none, which indicates to the editor to close that tab

Q. What happens if we change the type of a field in the parent, say an expression goes to a literal
A. The child tab for that expression (if there is one) will be deleted

Q. What happens if we clear out all the text from a child?
A. It is replaced with an empty dict, list or string depending on what type the child was

Q. What happens if we have an expression view and in the parent we change that to a scalar (str, int)
A. The child view is set to none, which indicates to the editor to close that tab

Q. What happens if we are editing in one view, and an external edit (that is reloaded) has a YAML
   error?
A. We refuse to reload and warn the user that an external edit would result in a YAML error
   and that error should be fixed, either by saving this working document, or fixing the document
   in the original external editor.
"""
from typing import Tuple, Dict, Callable
from enum import IntEnum

from ..implementationerror import ImplementationError
from .lineloader import parse_yaml_with_line_info, YNone, Ystr, Ydict, DocumentError
from .edit import Edit, EditMark
from .textview import TextView


class Contents(IntEnum):
    Unchanged = 0b1
    Changed = 0b10
    ParseSkipped = 0b100
    ParseSuccess = 0b1000
    ParseFail = 0b10000


class YamlView(TextView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._yaml = None
        self._last_good_yaml = None
        self.yaml_error = None
        self.children: Dict[Tuple[str, ...], TextView] = {}

    @property
    def yaml(self):
        if self._yaml is None:
            try:
                self._yaml = parse_yaml_with_line_info(self.raw_text, convert_to_lam=True) or Ydict.empty()
                self.yaml_error = None
                self._last_good_yaml = self._yaml
            except DocumentError as e:
                self._yaml = None
                self.yaml_error = e
        return self._yaml

    def __contains__(self, path: Tuple[str, ...]):
        sub_doc = self.yaml
        for p in path or []:
            if not isinstance(sub_doc, dict):
                return False
            if p in sub_doc:
                sub_doc = sub_doc[p]
            else:
                return False
        else:
            return True

    def __getitem__(self, path: Tuple[str, ...]):
        sub_doc = self.yaml
        for p in path or []:
            if sub_doc is None:
                raise ImplementationError("Component can not be None.")
            if not isinstance(sub_doc, dict):
                raise ImplementationError("We've got a bad path into a document.")
            sub_doc = sub_doc[p]
        return sub_doc

    def set_raw_text(self, raw_text):
        super().set_raw_text(raw_text)
        self._yaml = None

    def create_child_view(
            self, child_path: Tuple[str, ...],
            can_have_children=False,
            callback: Callable=None):
        # We will punt this to the root view
        if self.parent is not None:
            return self.root().create_child_view(
                child_path=self.inline_path + child_path,
                can_have_children=can_have_children,
                callback=callback)

        raw_text = self.get_raw_text_for_section(path=child_path)
        if can_have_children:
            child = YamlView(raw_text=raw_text,
                             file_path=self.file_path,
                             inline_path=child_path,
                             parent=self)
        else:
            child = TextView(raw_text=raw_text,
                             file_path=self.file_path,
                             inline_path=child_path,
                             parent=self)

        self.children[child_path] = child
        if callback is not None:
            callback(child)
        return child

    def get_raw_text_for_section(self, path: Tuple[str, ...]):
        value = self[path]

        start_line, end_line = value.start.line, value.end.line
        sl = start_line
        indent_level = len(self.raw_lines[sl]) - len(self.raw_lines[sl].lstrip())

        if isinstance(value, Ydict):  # Currently, sole use case is in steps
            if value.flow_style:
                if value == {}:
                    return ""
                else:
                    raise ImplementationError("Flow style elements can not be edited in a view.")
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

    def apply_from_child(self, raw_text: str, inline_path: Tuple[str, ...]):
        self.set_raw_text(
            raw_text="".join(
                self._apply_edit_to_lines(
                    self._project_raw_text_to_section_as_edit(raw_text=raw_text, path=inline_path)
                )))

        self._mark_children_for_deletion()
        self._remove_children_marked_for_deletion()

        for inline_path, child in self.children.items():
            child.set_raw_text(raw_text=self.get_raw_text_for_section(inline_path))

    # todo: V1.0 this code does not handle block text properly. Will extend for V2.0
    # Right now we worry mostly about "run" field of steps, which is a dict
    def _project_raw_text_to_section_as_edit(self, raw_text, path: Tuple[str, ...]):
        def _block_style(_ov):
            if isinstance(_ov, YNone): return False
            elif isinstance(_ov, Ydict): return not _ov.flow_style
            elif _ov.style != "": return True
            else: return False

        original_value = self[path]
        raw_text_lines = raw_text.splitlines(keepends=True)
        projected_text_lines = []

        start = EditMark(original_value.start.line, original_value.start.column)
        end = EditMark(original_value.end.line, original_value.end.column)

        block_style = _block_style(original_value)

        # Exception we make when going from block back to null style
        if raw_text == "" and block_style:
            start.column = 0
            return Edit(start, end, raw_text, raw_text_lines)

        if not raw_text.endswith("\n") and block_style:
            raw_text += "\n"
            raw_text_lines += ["\n"]
        # A user can remove this last new line from the editor. We need to add it back
        # otherwise we'll lose our block structure

        sl = original_value.start.line
        if len(self.raw_lines):
            indent_level = len(self.raw_lines[sl]) - len(self.raw_lines[sl].lstrip())
        else:
            indent_level = 0

        if isinstance(original_value, Ydict):  # Currently, sole use case is in steps
            if not block_style:
                if original_value == {}:
                    indent_level += 2
                    projected_text_lines += ["\n" + " " * indent_level]
                else:
                    raise ImplementationError("Should not be viewing flow style elements")
        else:  # Expressions and documentation
            if "\n" in raw_text:  # Multi-line
                if isinstance(original_value, YNone) or not block_style:
                    indent_level += 2
                    projected_text_lines += [" |-\n" + " " * indent_level]
            else:  # Single line, works regardless of block or flowstyle
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

        new_lines = \
            existing_lines[:edit.start.line] + \
            ([existing_lines[edit.start.line][:edit.start.column]]
             if edit.start.line < len(existing_lines) else []) + \
            lines_to_insert + \
            (([existing_lines[edit.end.line][edit.end.column:]] +
              (existing_lines[edit.end.line + 1:] if edit.end.line + 1 < len(existing_lines) else []))
             if edit.end.line < len(existing_lines) else [])

        return new_lines

    def _mark_children_for_deletion(self):
        for k, v in self.children.items():
            if k not in self:
                v.marked_for_deletion = True

    def _remove_children_marked_for_deletion(self):
        self.children = {k: v for k, v in self.children if not v.marked_for_deletion}
