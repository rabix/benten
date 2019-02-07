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
        self.directory_of_documents: Dict[str, Dict[([str], None), BentenWindow]] = {}

    def open_window(self, parent_path: str, inline_path: [str]):
        if parent_path not in self.directory_of_documents or \
                inline_path not in self.directory_of_documents[parent_path]:
            self.create_new_window(parent_path, inline_path)

        return self.directory_of_documents[parent_path][inline_path]
        # The receiver - BentenMainWidget - has to find out if this is an existing tab
        # or a new tab is needed

    def create_new_window(self, parent_path: str, inline_path: [str]):
        p_path = pathlib.Path(parent_path)
        if not p_path.exists():
            # Decision: we don't create a new document, we assume user error.
            # The sub-workflow must exist
            raise RuntimeError("Document {} does not exist".format(parent_path))

        bw = BentenWindow()

        if inline_path is None:
            # New root document
            raw_cwl = p_path.open("r").read()
            cwl_doc = CwlDoc(raw_cwl=raw_cwl, path=p_path, inline_path=inline_path)
            bw.set_document(cwl_doc=cwl_doc)
        else:
            # Find appropriate inline section of loaded document
            bw.set_document(
                cwl_doc=self.directory_of_documents[parent_path][None].
                    cwl_doc.get_nested_inline_step(inline_path))

        self.directory_of_documents[parent_path][inline_path] = bw

    def document_saved(self, parent_path: str, inline_path: [str]):
        pass