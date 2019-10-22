#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .linkedfiletype import CWLLinkedFile
from .basetype import IntelligenceContext, Intelligence, MapSubjectPredicate
from ..langserver.lspobjects import Range

import logging
logger = logging.getLogger(__name__)


class CWLLinkedSchemaDef(CWLLinkedFile):

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
        super().parse(doc_uri, node, intel_context, code_intel, problems, node_key, map_sp, key_range, value_range, requirements)
        if isinstance(self.node_dict, dict):
            if "name" in self.node_dict:
                name = self.prefix + "#" + self.node_dict.pop("name")
                code_intel.type_defs[name] = self.node_dict
                logger.debug(name)
