#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, MapSubjectPredicate, TypeCheck, Match

import logging
logger = logging.getLogger(__name__)


class CWLExpressionType(CWLBaseType):

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if isinstance(node, str):
            return TypeCheck(self)
        else:
            return TypeCheck(self, Match.No)

    # Future expansion: expression evaluation on hover
