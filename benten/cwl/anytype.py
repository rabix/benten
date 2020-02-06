#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, MapSubjectPredicate, TypeCheck
from .importincludetype import CWLImportInclude

import logging
logger = logging.getLogger(__name__)


class CWLAnyType(CWLBaseType):

    def __init__(self, name, type_dict):
        super().__init__(name)
        self.type_dict = type_dict
        # The Any type is special because it can be asked to
        # be anything. We need to carry the entire type dict
        # with us.

    def if_you_can_be_anything_be_this_kind(self, type_name):
        return self.type_dict.get(type_name)

    def all_possible_type_names(self):
        return list(self.type_dict.keys())

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if isinstance(node, dict) and "$import" in node:
            # Extra-special treatment for $imports
            return TypeCheck(CWLImportInclude(key="$import", import_context=""))
        else:
            # Special treatment for the any type. It agrees to everything
            return TypeCheck(self)
