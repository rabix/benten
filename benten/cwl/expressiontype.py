#  Copyright (c) 2019 Seven Bridges. See LICENSE

import re
from enum import IntEnum

import dukpy

from .basetype import (CWLBaseType, MapSubjectPredicate, TypeCheck, Match,
                       Intelligence, IntelligenceContext)
from ..langserver.lspobjects import Range, Hover
from ..code.intelligence import LookupNode

import logging
logger = logging.getLogger(__name__)


parameter_ref = re.compile(r"\$\((.*)\)", flags=re.DOTALL | re.M)
expression_ref = re.compile(r"\${(.*)\}", flags=re.DOTALL | re.M)


class CWLExpressionType(CWLBaseType):

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if isinstance(node, str):
            m = parameter_ref.match(node)
            if m is not None:
                return TypeCheck(
                    cwl_type=CWLExpression(
                        m.groups()[0], ExpressionType.ParameterReference))

            m = expression_ref.match(node)
            if m is not None:
                return TypeCheck(
                    cwl_type=CWLExpression(
                        m.groups()[0], ExpressionType.JSExpression))

        return TypeCheck(cwl_type=self, match=Match.No)


class ExpressionType(IntEnum):
    ParameterReference = 1
    JSExpression = 2


class CWLExpression(CWLBaseType):

    def __init__(self, expression: str, exp_type: ExpressionType):
        super().__init__("Expression")
        if exp_type is ExpressionType.ParameterReference:
            self.expression = \
                f"""
var runtime = dukpy['runtime'];
var inputs = dukpy['inputs'];
{expression}"""
        else:
            self.expression = \
                f"""
var runtime = dukpy['runtime'];
var inputs = dukpy['inputs'];
function benten_eval_func() {{
    {expression} 
}}; 
benten_eval_func()"""
        self.exp_type = exp_type
        self.execution_context = None

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if isinstance(node, str):
            if "$(" in node or "${" in node:
                return TypeCheck(cwl_type=self)

        return TypeCheck(cwl_type=self, match=Match.No)

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

        self.execution_context = code_intel.execution_context

        ln = LookupNode(loc=value_range)
        ln.intelligence_node = self
        code_intel.add_lookup_node(ln)

    # Future expansion: expression evaluation on hover
    def hover(self):
        try:
            res = dukpy.evaljs(self.execution_context.expression_lib + [self.expression],
                               runtime=self.execution_context.runtime,
                               inputs=self.execution_context.job_inputs)
        except dukpy.JSRuntimeError as e:
            res = f"{self.expression} -> {str(e)}"
            logger.error(res)

        return Hover(res)
