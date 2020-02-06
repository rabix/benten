#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
from urllib.parse import urlparse

from .linkedfiletype import CWLLinkedFile
from .basetype import IntelligenceContext, Intelligence, MapSubjectPredicate
from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity, Range

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

        if isinstance(self.node_dict, list):
            _type_list = self.node_dict
        elif isinstance(self.node_dict, dict):
            _type_list = [self.node_dict]
        else:
            problems += [
                Diagnostic(
                    _range=value_range,
                    message=f"Problem parsing SchemaDef file",
                    severity=DiagnosticSeverity.Error)
            ]
            return

        fname = pathlib.Path(urlparse(self.prefix).path).name

        for _type in _type_list:
            if "name" in _type:
                name = fname + "#" + _type.pop("name")
                code_intel.type_defs[name] = _type
