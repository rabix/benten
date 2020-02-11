#  Copyright (c) 2019 Seven Bridges. See LICENSE

import shlex
import pathlib

from .basetype import CWLBaseType, IntelligenceContext, Intelligence, MapSubjectPredicate
from ..langserver.lspobjects import Range, Location, CompletionItem, Hover
from .lib import validate_and_load_linked_file
from ..code.intelligence import LookupNode

import logging
logger = logging.getLogger(__name__)


class CWLLinkedFile(CWLBaseType):

    def __init__(self, prefix, extension=None):
        super().__init__("Linked file")
        self.prefix: str = prefix
        self.full_path: pathlib.Path = None
        self._contents: str = None
        self.node_dict: dict = None
        self.extension: str = extension

    def parse(self,
              doc_uri: str,
              node,
              intel_context: IntelligenceContext,
              code_intel: Intelligence,
              problems: list,
              node_key: str = None,
              map_sp: MapSubjectPredicate = None,
              key_range: Range = None,
              value_range: Range = None,
              requirements=None):

        self.full_path, self._contents, self.node_dict = \
            validate_and_load_linked_file(doc_uri, self.prefix, value_range, problems)
        ln = LookupNode(loc=value_range)
        ln.intelligence_node = self
        code_intel.add_lookup_node(ln)

    def hover(self):
        return Hover(self._contents)

    def definition(self):
        if isinstance(self.full_path, pathlib.Path):
            return Location(self.full_path.as_uri())

    def completion(self):
        return [
            CompletionItem(label=file_path)
            for file_path in self._file_picker()
        ]

    def _file_picker(self):

        # This is an http path, not a file system path
        if not isinstance(self.full_path, pathlib.Path):
            return []

        # We use .split( ... ) so we can handle the case for run: .    # my/commented/path
        # and other such shenanigans
        _prefix = shlex.split(self.prefix, comments=True)[0]

        path = self.full_path
        if not path.is_dir():
            path = path.parent

        if not path.exists():
            logger.error(f"No path called: {path}")
            return []

        # This is a workaround to the issue of having a dangling "." in front of the path
        pre = "/" if _prefix in [".", ".."] else ""

        return (pre + str(p.relative_to(path))
                for p in path.iterdir()
                if p.is_dir() or (self.extension is None or p.suffix == self.extension))
