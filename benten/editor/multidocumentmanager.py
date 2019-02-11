"""This class helps encapsulate the operations we have to do to ensure synchronicity between
views on the same underlying document (nested inline steps).

Responsibilities

1. Keep track of the underlying document url and (for inline steps) the internal path to the
   document for each BentenWindow.
2. When a request to open a document is received, arbitrate if a new window is needed or if
   an existing window suffices
3. When an edit is executed traverse the list of windows and apply edits to all sibling windows
   as needed. Close windows referencing deleted steps as needed.
4. Manage saving and (re)loading of documents
5. [Future version] Keep track of all sub-workflows in a given document and update the interface
   when this external file changes.

"""
from typing import List, Set, Dict, Tuple, Optional
import pathlib

from benten.editor.bentenwindow import BentenWindow
from benten.editing.cwldoc import CwlDoc


class MultiDocumentManager:
    def __init__(self):
        self.directory_of_documents: Dict[str, Dict[(Tuple[str], None), BentenWindow]] = {}

    def open_window(self, parent_path: pathlib.Path, inline_path: Tuple[str]):
        path_str = parent_path.resolve().as_uri()
        if path_str not in self.directory_of_documents or \
                inline_path not in self.directory_of_documents[path_str]:
            self.create_new_window(parent_path, inline_path)

        return self.directory_of_documents[path_str][inline_path]
        # The receiver - BentenMainWidget - has to find out if this is an existing tab
        # or a new tab is needed

    def create_new_window(self, parent_path: pathlib.Path, inline_path: Tuple[str, ...]):
        if not parent_path.exists():
            # Decision: we don't create a new document, we assume user error.
            # The sub-workflow must exist
            raise RuntimeError("Document {} does not exist".format(parent_path))

        bw = BentenWindow()
        path_str = parent_path.resolve().as_uri()

        if inline_path is None or len(inline_path) == 0:
            # New root document
            self.directory_of_documents[path_str] = {}
            raw_cwl = parent_path.open("r").read()
            cwl_doc = CwlDoc(raw_cwl=raw_cwl, path=parent_path, inline_path=None)
            bw.set_document(cwl_doc=cwl_doc)
        else:
            # Find appropriate inline section of loaded document
            bw.set_document(
                cwl_doc=self.directory_of_documents[path_str][None].
                    cwl_doc.get_nested_inline_step(inline_path))

        self.directory_of_documents[path_str][inline_path] = bw

    def nested_document_edited(self, cwl_doc: CwlDoc):
        path_str = cwl_doc.path.resolve().as_uri()
        inline_path = cwl_doc.inline_path

        base_bw = self.directory_of_documents[path_str][None]

        if inline_path is not None and len(inline_path) > 0:
            new_base_cwl = base_bw.cwl_doc.get_raw_cwl_of_base_after_nested_edit(
                inline_path=inline_path, new_cwl=cwl_doc.raw_cwl)
            base_cwl_doc = CwlDoc(raw_cwl=new_base_cwl, path=cwl_doc.path, inline_path=None)
            base_bw.set_document(cwl_doc=base_cwl_doc)

        base_cwl_doc = base_bw.cwl_doc
        for nested_inline_path, nested_bw in self.directory_of_documents[path_str].items():
            if nested_inline_path is None: continue
            nested_bw.set_document(cwl_doc=base_cwl_doc.get_nested_inline_step(nested_inline_path))

    def document_saved(self, parent_path: pathlib.Path, inline_path: [str]):
        pass
