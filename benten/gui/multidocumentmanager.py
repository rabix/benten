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
from typing import Dict, Tuple, List
import pathlib

from .bentenwindow import BentenWindow
from ..editing.cwldoc import CwlDoc
from ..sbg.sbgcwldoc import SBGCwlDoc
from ..editing.documentmanager import DocumentManager


class MDMUnit:
    def __init__(self, bw: BentenWindow, doc_man: (DocumentManager, None)):
        self.window: BentenWindow = bw
        self.doc_man: DocumentManager = doc_man

    def set_document(self, cwl_doc: CwlDoc):
        self.window.set_document(cwl_doc=cwl_doc)
        if self.doc_man is not None:
            self.doc_man.set_document(cwl_doc=cwl_doc)


class MultiDocumentManager:
    def __init__(self, benten_main_window):
        self.directory_of_documents: Dict[str, Dict[(Tuple[str], None), MDMUnit]] = {}
        self.bmw = benten_main_window

    def lookup_parent_doc(self, cwl_doc: CwlDoc):
        return next((mdmu[None] for mdmu in self.directory_of_documents.values()
                    if mdmu[None].doc_man.path == cwl_doc.path), None)

    def windows_for_this_doc(self, cwl_doc: CwlDoc, bw_list: List[BentenWindow]):
        return [bw for bw in bw_list if bw.cwl_doc.path == cwl_doc.path]

    def lookup_unsaved_docs(self):
        return [mdmu[None] for mdmu in self.directory_of_documents.values()
                if not mdmu[None].doc_man.status()["saved"]]

    def open_window(self, parent_path: pathlib.Path, inline_path: Tuple[str]):
        path_str = parent_path.resolve().as_uri()
        if path_str not in self.directory_of_documents or \
                inline_path not in self.directory_of_documents[path_str]:
            path_str = self.create_new_window(parent_path, inline_path)

        return self.directory_of_documents[path_str][inline_path].window
        # The receiver - BentenMainWidget - has to find out if this is an existing tab
        # or a new tab is needed

    def create_new_window(self, parent_path: pathlib.Path, inline_path: Tuple[str, ...]):
        if not parent_path.exists():
            # Decision: we don't create a new document, we assume user error.
            # The sub-workflow must exist
            raise RuntimeError("Document {} does not exist".format(parent_path))

        mdm_unit = MDMUnit(bw=BentenWindow(benten_main_window=self.bmw), doc_man=None)
        path_str = parent_path.resolve().as_uri()

        if inline_path is None or len(inline_path) == 0:
            # New root document
            raw_cwl = parent_path.open("r").read()
            cwl_format = SBGCwlDoc.detect_cwl_format(raw_cwl)

            if cwl_format == "json":
                new_path = pathlib.Path(parent_path.parent, parent_path.name + ".cwl")
                path_str = new_path.resolve().as_uri()
                cwl_doc = SBGCwlDoc(raw_json=raw_cwl, new_path=new_path, inline_path=None,
                                    api=self.bmw.api)
            else:
                cwl_doc = SBGCwlDoc(raw_cwl=raw_cwl, path=parent_path, inline_path=None,
                                    api=self.bmw.api)

            doc_man = DocumentManager(cwl_doc=cwl_doc)
            if cwl_format == "json":
                doc_man.save()  # This converted document only exists in memory upto now

            #mdm_unit = MDMUnit(bw=BentenWindow(), doc_man=doc_man)
            mdm_unit.doc_man = doc_man
            mdm_unit.set_document(cwl_doc=cwl_doc)
            self.directory_of_documents[path_str] = {}
        else:
            # Find appropriate inline section of loaded document
            mdm_unit.set_document(
                cwl_doc=self.directory_of_documents[path_str][None].
                    window.cwl_doc.get_nested_inline_step(inline_path))

        self.directory_of_documents[path_str][inline_path] = mdm_unit
        return path_str

    def _nested_documents_are_open(self, path_str):
        return len(self.directory_of_documents[path_str]) > 1

    def apply_document_edits(self, cwl_doc: CwlDoc) -> DocumentManager:
        path_str = cwl_doc.path.resolve().as_uri()
        inline_path = cwl_doc.inline_path

        base = self.directory_of_documents[path_str][None]

        if inline_path is not None and len(inline_path) > 0:
            new_base_cwl = base.window.cwl_doc.get_raw_cwl_of_base_after_nested_edit(
                inline_path=inline_path, new_cwl=cwl_doc.raw_cwl)
            if new_base_cwl == base.window.cwl_doc.raw_cwl:
                return self.directory_of_documents[path_str][None].doc_man

            base_cwl_doc = CwlDoc(raw_cwl=new_base_cwl, path=cwl_doc.path, inline_path=None)
            base_cwl_doc.compute_cwl_dict()  # We're gonna need this to propagate the edits
            base.set_document(cwl_doc=base_cwl_doc)
        else:
            # The window already knows about this, we just need to let the manager know
            self.directory_of_documents[path_str][None].doc_man.set_document(cwl_doc=cwl_doc)

        base_cwl_doc = base.window.cwl_doc
        for nested_inline_path, nested_bw in self.directory_of_documents[path_str].items():
            if nested_inline_path is None: continue
            nested_bw.set_document(cwl_doc=base_cwl_doc.get_nested_inline_step(nested_inline_path))

        # Regardless, return the base document for save decisions
        return self.directory_of_documents[path_str][None].doc_man
