"""This class represents a main CwlDoc across edits, keeping track of whether it's been saved
and whether the version on disk has been altered outside the editor.

0. It only deals with the raw_cwl field of the cwl_doc
1. It does I/O: it can load from and save to disk though the loading is not allowed to
   alter the original contents
2. It can load the text from disk and indicate if the contents are different from itself
"""
from .cwldoc import CwlDoc


class DocumentManager:
    def __init__(self, cwl_doc: CwlDoc):
        self.cwl_doc = None
        self.set_document(cwl_doc=cwl_doc)
        self.last_saved_doc = self.cwl_doc.raw_cwl
        # We use this to check if the doc has been modified outside of Benten
        # We start out assuming we've got the freshest doc loaded from disk

    def set_document(self, cwl_doc: CwlDoc):
        if cwl_doc.inline_path:
            raise RuntimeError("This class should only handle base documents")
        self.cwl_doc = cwl_doc

    @property
    def raw_cwl(self):
        return self.cwl_doc.raw_cwl

    @property
    def path(self):
        return self.cwl_doc.path

    @property
    def inline_path(self):
        return self.cwl_doc.inline_path

    def status(self):
        _status = {
            "changed_externally": False,
            "saved": False
        }

        raw_cwl_on_disk = self.cwl_doc.path.resolve().open("r").read()

        if raw_cwl_on_disk != self.last_saved_doc:
            _status["changed_externally"] = True
        elif raw_cwl_on_disk == self.cwl_doc.raw_cwl:
            _status["saved"] = True

        return _status

    def save(self):
        self.cwl_doc.path.resolve().open("w").write(self.cwl_doc.raw_cwl)
        self.last_saved_doc = self.cwl_doc.raw_cwl
