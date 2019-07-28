#  Copyright (c) 2019 Seven Bridges. See LICENSE

import shlex

from .basetype import CWLBaseType, IntelligenceContext, Intelligence, MapSubjectPredicate
from ..langserver.lspobjects import Range, Location, CompletionItem
from .lib import check_linked_file
from ..code.intelligence import LookupNode

import logging
logger = logging.getLogger(__name__)


class CWLLinkedFile(CWLBaseType):

    def __init__(self, prefix, extension=None):
        super().__init__("Linked file")
        self.prefix = prefix
        self.full_path = None
        self.extension = extension

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

        self.full_path = check_linked_file(doc_uri, self.prefix, value_range, problems)
        ln = LookupNode(loc=value_range)
        ln.intelligence_node = self
        code_intel.add_lookup_node(ln)

    def definition(self):
        return Location(self.full_path.as_uri())

    def completion(self):
        return [
            CompletionItem(label=file_path)
            for file_path in self._file_picker()
        ]

    def _file_picker(self):

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
