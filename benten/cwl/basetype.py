#  Copyright (c) 2019 Seven Bridges. See LICENSE

from dataclasses import dataclass
from enum import IntEnum

from ..code.intelligence import IntelligenceNode, Intelligence


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
              parent_intel_node: IntelligenceNode,
              code_intel: Intelligence,
              problems: list,
              node_key: str=None,
              map_sp: MapSubjectPredicate=None,
              requirements=None):
        pass
