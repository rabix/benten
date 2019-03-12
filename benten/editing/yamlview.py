"""This abstracts out a framework for keeping track of views and computing the backward and
forward edit projections from the view. For now we just handle block elements."""
from typing import Tuple, Dict
from abc import ABC, abstractmethod

from ..implementationerror import ImplementationError
from .edit import Edit, EditMark
from .yamldoc import TextType, PlainText, YamlDoc, Contents


class EditorInterface(ABC):

    @abstractmethod
    def set_text(self, raw_text: str):
        pass

    @abstractmethod
    def get_text(self):
        pass

    @abstractmethod
    def apply_edit(self, edit: Edit):
        pass

    @abstractmethod
    def mark_for_deletion(self):
        pass


class YamlView:
    def __init__(self, raw_text: str, path: Tuple[str], text_type: TextType):
        # self.anchor: Anchor = None
        self.path = path
        self.doc = YamlDoc(raw_text) if text_type == TextType.process else PlainText(raw_text)
        self.attached_editor: EditorInterface = None
        self.parent: 'YamlView' = None
        self.children: Dict[Tuple[str], YamlView] = {}

    def __contains__(self, path: Tuple[str]):
        return path in self.children

    def get(self, path: Tuple[str]):
        return self.children.get(path, None)

    def get_originating_edit(self):
        """Called when manual or programmatic edit is signalled by attached editor"""
        raw_text = self.attached_editor.get_text()
        parse_result = self.doc.set_raw_text_and_reparse(raw_text)
        if parse_result & Contents.ParseSuccess:
            self.propagate_edit_to_ancestor()
            self.propagate_edits_to_children()

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

    def create_child_view(self, path: Tuple[str], editor: EditorInterface):
        if not isinstance(self.doc, YamlDoc):
            raise ImplementationError("Only processes can have child views")

        if self.doc.yaml_error is not None:
            raise ImplementationError("Processes with YAML errors can't spawn child views")

        child_view = YamlView(
            raw_text=self.doc.get_raw_text_for_section(path),
            path=path, text_type=YamlDoc.infer_section_type(path))
        child_view.attached_editor = editor
        editor.set_text(child_view.doc.raw_text)

        self.children[path] = child_view
