#  Copyright (c) 2019 Seven Bridges. See LICENSE

import re
from enum import IntEnum

import dukpy

from .basetype import (CWLBaseType, MapSubjectPredicate, TypeCheck, Match,
                       Intelligence, IntelligenceContext)
from ..langserver.lspobjects import Range, Hover, Location
from ..code.intelligence import LookupNode
from ..code.executioncontext import basic_example_value

import logging
logger = logging.getLogger(__name__)


parameter_ref = re.compile(r"(^.*?)\$\((.*)\)(.*?$)", flags=re.DOTALL | re.M)
expression_ref = re.compile(r"(^.*?)\${(.*)\}(.*?$)", flags=re.DOTALL | re.M)


class CWLExpressionType(CWLBaseType):

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if isinstance(node, str):
            m = parameter_ref.match(node)
            if m is not None:
                return _create_expression(m, ExpressionType.ParameterReference)

            m = expression_ref.match(node)
            if m is not None:
                return _create_expression(m, ExpressionType.JSExpression)

        return TypeCheck(cwl_type=self, match=Match.No)


def _create_expression(m, exp_type):
    grp = m.groups()
    return TypeCheck(
        cwl_type=CWLExpression(grp[1], exp_type, bracketing_terms=(grp[0], grp[2])))


class ExpressionType(IntEnum):
    ParameterReference = 1
    JSExpression = 2


class CWLExpression(CWLBaseType):

    def __init__(self, expression: str, exp_type: ExpressionType, bracketing_terms=None):
        super().__init__("Expression")
        self.bracketing_terms = bracketing_terms or ["", ""]
        self.self_path = ()  # the path to the 'self' variable as described in CWL specs
        if exp_type is ExpressionType.ParameterReference:
            self.expression = \
                f"""
var runtime = dukpy['runtime'];
var inputs = dukpy['inputs'];
var self = dukpy['cwl_self'];
{expression}"""
        else:
            self.expression = \
                f"""
var runtime = dukpy['runtime'];
var inputs = dukpy['inputs'];
var self = dukpy['cwl_self'];
function benten_eval_func() {{
    {expression} 
}}; 
benten_eval_func()"""
        self.exp_type = exp_type
        self.execution_context = None

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

        # Deal with filling out self
        if intel_context.path[-1] in ["secondaryFiles"]:
            self.self_path = ('inputs', intel_context.path[-2])

        if intel_context.path[-1] in ["position", "valueFrom"]:
            if intel_context.path[-2] == "inputBinding":
                self.self_path = ('inputs', intel_context.path[-3])

        if intel_context.path[-1] in ["outputEval"]:
            self.self_path = ('outputs', intel_context.path[-3])
            logger.warning("Benten can't properly simulate globbed files yet")
            pass
            # todo: Check for the glob and then simulate globbed files

        ln = LookupNode(loc=value_range)
        ln.intelligence_node = self
        code_intel.add_lookup_node(ln)

    def hover(self):
        job_inputs = self.execution_context.job_inputs
        cwl_self = None

        if self.self_path:
            if self.self_path[0] == 'inputs':
                cwl_self = job_inputs[self.self_path[1]]
            if self.self_path[0] == 'outputs':
                cwl_self = [basic_example_value(self.self_path[1] + "/" + str(i), "File")
                            for i in range(4)]

        if job_inputs:
            try:
                res = dukpy.evaljs(self.execution_context.expression_lib + [self.expression],
                                   runtime=self.execution_context.runtime,
                                   inputs=job_inputs,
                                   cwl_self=cwl_self)

                if res is None and self.exp_type == ExpressionType.JSExpression:
                    res = "Got a 'null' result. Do you have a `return` for your JS expression?"
                else:
                    res = self.bracketing_terms[0] + str(res) + self.bracketing_terms[1]

            except dukpy.JSRuntimeError as e:
                res = str(e).splitlines()[0]
                logger.error(res)
        else:
            res = "Job inputs have not been filled out"

        return Hover(res)

    def definition(self):
        # Hijacking this to show the sample inputs file
        return Location(self.execution_context.get_sample_data_file_path().as_uri())
