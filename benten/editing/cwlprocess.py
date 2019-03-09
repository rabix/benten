"""This represents a CWL document that we can take sub-views of. It itself can be a sub-view.

It's main responsibility is to make sure edits are synchronized across different
views of a document. As such we do not implement process type specific logic here, but make
it somewhat general.

There are two types of fragments
    - those that can be sub-viewed further and
    - those that can not.
This base type represents a document that can not be sub-viewed further. The CwlProcess mixin
represents a document that can be sub-viewed further and adds the ability to create new views
from it.

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

from typing import Union, Tuple, Dict
import pathlib

from .cwldoc import CwlDoc, ViewType
from .edit import Edit, EditMark
from ..implementationerror import ImplementationError
from .lineloader import (parse_yaml_with_line_info,
                         DocumentError,
                         lookup, reverse_lookup,
                         Ydict, Ylist, Ystr)


class LockedDueToYAMLErrors(Exception):
    pass


class UnableToCreateView(Exception):
    pass


class CwlProcess(CwlDoc):
    def __init__(self):
        super().__init__()

        self.parent_view: Union[CwlDoc, 'CwlProcess'] = None
        self.cwl_dict = None
        self.cwl_lines = None
        self.yaml_error = None

        self.last_known_good_dict = None
        self.last_saved_raw_cwl = None

        self.child_views: Dict[Tuple[Union[str, int], ...], CwlDoc] = {}

    # There are two ways to create a view
    # a) Load it from a file on disk, creating a parent view
    @classmethod
    def create_from_file(cls, path: pathlib.Path) -> 'CwlProcess':
        view = cls()
        view.view_type = ViewType.Process
        view.raw_cwl = path.resolve().open("r").read()
        view.last_saved_raw_cwl = view.raw_cwl
        view.cwl_lines = view.raw_cwl.splitlines(keepends=True)
        view.path = path
        return view

    # b) Create it as a view into a parent document -> child view

    # Either from a document position
    # def create_child_view_from_cursor(self, line, column) -> CwlDoc:
    #     self.compute_cwl_dict()
    #     inline_path, _ = reverse_lookup(line, column, self.cwl_dict)
    #     return self.create_child_view_from_path((self.inline_path or ()) + inline_path)

    # Or from a path
    def create_child_view_from_path(
            self, inline_path: Tuple[Union[str, int], ...]) -> CwlDoc:
        if self.parent_view is not None:
            return self.parent_view.create_child_view_from_path((self.inline_path or ()) + inline_path)

        if inline_path in self.child_views:
            return self.child_views[inline_path]

        self.compute_cwl_dict()
        if self.is_invalid():
            raise LockedDueToYAMLErrors()

        raw_cwl, view_type = self._raw_cwl_from_inline_path(inline_path)
        if view_type == ViewType.Process:
            view = type(self)()
            view.last_saved_raw_cwl = view.raw_cwl
            view.cwl_lines = raw_cwl.splitlines(keepends=True)
        else:
            view = CwlDoc()

        view.raw_cwl, view.view_type = raw_cwl, view_type
        view.path = self.path
        view.inline_path = inline_path

        view.parent_view = self
        self.child_views[inline_path] = view

        return view

    def is_invalid(self):
        return self.yaml_error is not None

    def changed_on_disk(self):
        if self.parent_view is not None:
            return self.parent_view.changed_on_disk()

        raw_cwl_on_disk = self.path.resolve().open("r").read()
        return raw_cwl_on_disk != self.last_saved_raw_cwl

    def needs_saving(self):
        if self.parent_view is not None:
            return self.parent_view.needs_saving()

        return self.last_saved_raw_cwl != self.raw_cwl

    def status(self):
        if self.parent_view is not None:
            return self.parent_view.status()

        _status = {
            "changed_externally": False,
            "saved": False
        }

        raw_cwl_on_disk = self.path.resolve().open("r").read()

        if raw_cwl_on_disk != self.last_saved_raw_cwl:
            _status["changed_externally"] = True
        elif raw_cwl_on_disk == self.raw_cwl:
            _status["saved"] = True

        return _status

    def save(self):
        if self.parent_view is not None:
            return self.parent_view.save()

        self.path.resolve().open("w").write(self.raw_cwl)
        self.last_saved_raw_cwl = self.raw_cwl

    def load(self):
        if self.parent_view is not None:
            return self.parent_view.load()

        self.raw_cwl = self.path.resolve().open("r").read()
        self.last_saved_raw_cwl = self.raw_cwl
        self.propagate_edits()

    def apply_raw_text(self, raw_cwl: str, inline_path: Tuple[Union[str, int], ...]=None):
        if inline_path is None:
            inline_path = self.inline_path
        if self.parent_view is not None:
            return self.parent_view.apply_raw_text(raw_cwl=raw_cwl, inline_path=inline_path)

        self.set_raw_cwl(self.apply_edit_to_text(self.get_edit_from_new_text(raw_cwl, inline_path)))
        self.propagate_edits()

    def apply_edit(self, edit: Edit, inline_path: Tuple[Union[str, int], ...]=None):
        self.apply_raw_text(self.apply_edit_to_text(edit), inline_path)

    def set_raw_cwl(self, raw_cwl):
        self.raw_cwl = raw_cwl
        self.cwl_lines = self.raw_cwl.splitlines(keepends=True)
        self.cwl_dict = None

    # I want to be conscious and in control of when this (semi)expensive computation is being done
    # But I'd don't want to accidentally do it twice
    def compute_cwl_dict(self):
        if self.cwl_dict is not None:
            return

        if self.view_type is not ViewType.Process:
            raise ImplementationError("Code should not try and parse expression or document fragments")

        try:
            self.cwl_dict = parse_yaml_with_line_info(self.raw_cwl, convert_to_lam=True) or Ydict.empty()
        except DocumentError as e:
            self.yaml_error = e
            return

        self.last_known_good_dict = self.cwl_dict

    def type(self):
        return {
            ViewType.Process: (self.cwl_dict or {}).get("class", "unknown"),
            ViewType.Doc: "Doc",
            ViewType.Expression : "Expression"
        }.get(self.view_type)


    #
    # Implementation details ...
    #

    def get_edit_from_new_text(self, raw_cwl: str, inline_path: Tuple[Union[str, int], ...]=None) -> Edit:
        if inline_path is None:
            inline_path = self.inline_path

        if self.parent_view is not None:
            return self.parent_view.get_edit_from_new_text(raw_cwl, inline_path)
        else:
            return self._get_edit_projected_to_base_document(raw_cwl, inline_path)

    def apply_edit_to_text(self, edit: Edit):
        existing_lines = self.cwl_lines
        lines_to_insert = edit.text.splitlines(keepends=True)

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

        return "".join(new_lines)

    def propagate_edits(self):
        if self.parent_view is not None:
            return self.parent_view.propagate_edits()

        if len(self.child_views):
            self.compute_cwl_dict()
            # Todo: trap YAML errors and lock moving away from tab -> do this in original tab
            for cv in self.child_views.values():
                raw_cwl, cv.view_type = self._raw_cwl_from_inline_path(cv.inline_path)
                cv.set_raw_cwl(raw_cwl=raw_cwl)

    def _raw_cwl_from_inline_path(self, inline_path) -> (CwlDoc, ViewType):
        value = lookup(self.cwl_dict, inline_path)
        inferred_type = ViewType.Doc

        start_line, end_line = value.start.line, value.end.line
        sl = start_line
        indent_level = len(self.cwl_lines[sl]) - len(self.cwl_lines[sl].lstrip())

        if isinstance(value, Ydict):  # Currently, sole use case is in steps
            inferred_type = ViewType.Process
            if value.flow_style:
                if value == {}:
                    return "", inferred_type
                else:
                    raise UnableToCreateView("Flow style elements can not be edited in a view")
        elif isinstance(value, Ystr):  # Single line expressions and documentation
            # todo: check for expressions
            if value.style == "":
                return value, inferred_type

        lines_we_need = self.cwl_lines[start_line:end_line]
        lines = [
            l[indent_level:] if len(l) > indent_level else "\n"
            for l in lines_we_need
        ]
        # All lines with text have the given indent level or more, so they are not an issue
        # Blank lines, however, can be zero length, hence the exception.
        return "".join(lines), inferred_type

    def _get_edit_projected_to_base_document(
            self, new_cwl: str, inline_path: Tuple[Union[str, int], ...]=None) -> Union[Edit, None]:
        original_value = lookup(self.cwl_dict, inline_path)

        text_lines = []

        start = EditMark(original_value.start.line, original_value.start.column)
        end = EditMark(original_value.end.line, original_value.end.column)

        sl = original_value.start.line
        if len(self.cwl_lines):
            indent_level = len(self.cwl_lines[sl]) - len(self.cwl_lines[sl].lstrip())
        else:
            indent_level = 0

        if isinstance(original_value, Ydict):  # Currently, sole use case is in steps
            if original_value.flow_style:
                if original_value == {}:
                    if new_cwl == "":
                        return None
                    else:
                        indent_level += 2
                        text_lines += ["\n" + " " * indent_level]
                else:
                    raise ImplementationError("Should not be viewing flow style elements")
        elif isinstance(original_value, Ystr):  # Expressions and documentation
            if original_value.style == "" and "\n" in new_cwl:
                text_lines += "|-"
                indent_level += 2

        text_lines += [((' '*indent_level) if len(l) > 1 and n > 0 else "") + l
                       for n, l in enumerate(new_cwl.splitlines(keepends=True))]
        # 1. First line should have no indent - the cursor position takes care of that
        # 2. All lines with text have the given indent level or more, so they are not an issue
        #    Blank lines, however, can be zero length, hence the exception.

        return Edit(start, end, "".join(text_lines))
        # Notice that we haven't changed the contents of the doc, just created an Edit object
        # It is up to the GUI part to now take this edit, apply it to the base document and
        # then chain these to all the children.
