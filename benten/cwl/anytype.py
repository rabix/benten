#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .basetype import CWLBaseType, Workflow, Intelligence, MapSubjectPredicate, TypeCheck, Match
from ..langserver.lspobjects import Range, CompletionItem, Diagnostic, DiagnosticSeverity
from ..code.intelligence import LookupNode

import logging
logger = logging.getLogger(__name__)


class CWLAnyType(CWLBaseType):

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        # Special treatment for the any type. It agrees to everything
        return TypeCheck(self)
