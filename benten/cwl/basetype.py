#  Copyright (c) 2019 Seven Bridges. See LICENSE

from dataclasses import dataclass
from enum import IntEnum

from ..langserver.lspobjects import Range
from ..code.intelligence import IntelligenceNode, IntelligenceContext, Intelligence
from ..code.workflow import Workflow


class MapSubjectPredicate:

    def __init__(self, subject, predicate):
        self.subject = subject
        self.predicate = predicate


class Match(IntEnum):
    Yes = 0
    Maybe = 1
    No = 2


@dataclass
class TypeCheck:
    cwl_type: 'CWLBaseType'
    match: Match = Match.Yes
    missing_req_fields: list = None
    missing_opt_fields: list = None


class CWLBaseType(IntelligenceNode):

    def __init__(self, name):
        super().__init__()
        self.name = name

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        pass

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
        pass
