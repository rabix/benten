"""This abstracts out a framework for keeping track of views and computing the backward and
forward edit projections from the view. For now we just handle block elements.

This represents a CWL document that we can take sub-views of. It itself can be a sub-view.

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
from typing import Tuple, Dict
from abc import abstractmethod

from ..implementationerror import ImplementationError
from .edit import Edit, EditMark
from .yamldoc import TextType, PlainText, YamlDoc, Contents


class EditorInterface:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attached_view: 'YamlView' = None
        # This is a function the Editor can call when it needs the view to know about
        # edits that happened in it (manually or programmatically)
        self.locked = False
        self.delete_me = False

    # This is meant to replace the whole text in one go
    # Should not trigger any downstream edit events
    @abstractmethod
    def set_text(self, raw_text: str):
        pass

    @abstractmethod
    def get_text(self):
        pass

    # This is meant to replace targeted text
    # Should not trigger any downstream edit events
    @abstractmethod
    def apply_edit(self, edit: Edit):
        pass

    def mark_for_deletion(self):
        self.delete_me = True

    def push_changes(self):
        return self.attached_view.fetch_from_editor()

    def parse_yaml(self):
        return self.attached_view.doc.parse_yaml()

    def get_yaml(self):
        return self.attached_view.doc.yaml

    def yaml_error(self):
        return self.attached_view.doc.yaml_error

    def yaml_doc(self):
        return self.attached_view.doc


class YamlView:
    def __init__(self, raw_text: str, path: Tuple[str, ...],
                 text_type: TextType, editor: EditorInterface,
                 full_readable_path: Tuple[str, ...]=None,
                 parent: 'YamlView'=None):
        self.path = path
        self.full_readable_path = full_readable_path
        self.doc = YamlDoc(raw_text) if text_type == TextType.process else PlainText(raw_text)
        self.attached_editor: EditorInterface = editor
        self.attached_editor.set_text(raw_text)
        self.attached_editor.attached_view = self
        # The communication is bidirectional - the attached editor needs to know to call us
        self.parent: 'YamlView' = parent
        self.children: Dict[Tuple[str, ...], YamlView] = {}

    def __contains__(self, path: Tuple[str, ...]):
        return path in self.children

    def get_root(self):
        if self.parent is None:
            return self
        else:
            return self.parent.get_root()

    def get(self, path: Tuple[str, ...]):
        return self.children.get(path, None)

    def fetch_from_editor(self):
        """Called when manual or programmatic edit is signalled by attached editor"""
        raw_text = self.attached_editor.get_text()
        parse_result = self.doc.set_raw_text_and_reparse(raw_text)
        if parse_result & Contents.ParseSuccess:
            self.attached_editor.locked = False
            self.propagate_edit_to_ancestor()
            self.propagate_edits_to_children()
        elif parse_result & Contents.Unchanged:
            return parse_result
        else:
            self.attached_editor.locked = True
        return parse_result

    def propagate_edit_to_ancestor(self):
        if self.parent is None:
            return
        self.parent.attached_editor.apply_edit(
            self.parent.doc.set_section_from_raw_text(self.doc.raw_text, self.path))
        self.parent.propagate_edit_to_ancestor()

    def propagate_edits_to_children(self):
        if not isinstance(self.doc, YamlDoc):
            return

        self.doc.parse_yaml()  # The propagate call is recursive, and the children need to be parsed
        deleted_child_paths = []
        for path, child_view in self.children.items():
            if path in self.doc:
                new_child_text = self.doc.get_raw_text_for_section(path)
                edit = YamlDoc.edit_from_quick_diff(
                    child_view.doc.raw_lines,
                    new_child_text.splitlines(keepends=True))
                child_view.attached_editor.apply_edit(edit)
                child_view.doc.set_raw_text(new_child_text)
                child_view.propagate_edits_to_children()
            else:
                child_view.attached_editor.mark_for_deletion()
                deleted_child_paths += [path]

        for path in deleted_child_paths:
            self.children.pop(path)

    def create_child_view(self, path: Tuple[str, ...], editor: EditorInterface) -> 'YamlView':
        if not isinstance(self.doc, YamlDoc):
            raise ImplementationError("Only processes can have child views")

        if self.doc.yaml_error is not None:
            raise ImplementationError("Processes with YAML errors can't spawn child views")

        text_type = YamlDoc.infer_section_type(path)
        child_view = YamlView(
            raw_text=self.doc.get_raw_text_for_section(path),
            path=path, text_type=text_type,
            full_readable_path=(self.full_readable_path or ()) +
                               ((path[-2],) if text_type == TextType.process else (path,)),
            editor=editor, parent=self)

        self.children[path] = child_view
        return child_view
