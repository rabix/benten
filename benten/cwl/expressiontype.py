#  Copyright (c) 2019 Seven Bridges. See LICENSE

import re
from enum import IntEnum

import dukpy

from .basetype import (CWLBaseType, MapSubjectPredicate, TypeCheck, Match,
                       Intelligence, IntelligenceContext)
from ..langserver.lspobjects import Range, Hover, Location
from ..code.intelligence import LookupNode

import logging
logger = logging.getLogger(__name__)


parameter_ref = re.compile(r"\$\(((.(?<!\$({|\()))*)\)", flags=re.DOTALL | re.M)
expression_ref = re.compile(r"\${((.(?<!\$({|\()))*)}", flags=re.DOTALL | re.M)


class CWLExpressionType(CWLBaseType):

    def check(self, node, node_key: str=None, map_sp: MapSubjectPredicate=None) -> TypeCheck:
        if isinstance(node, str):
            if "$(" in node or "${" in node:
                return TypeCheck(cwl_type=CWLExpression(node))

        return TypeCheck(cwl_type=self, match=Match.No)


class ExpressionType(IntEnum):
    PlainString = 0
    ParameterReference = 1
    JSExpression = 2


class CWLExpression(CWLBaseType):

    def __init__(self, text: str):
        super().__init__("Expression")
        self.text = text
        self.intel_context = None
        self.execution_context = None
        # self.self_path = ()  # the path to the 'self' variable as described in CWL specs
        self.range = None

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

        self.intel_context = intel_context
        self.execution_context = code_intel.execution_context
        self.range = value_range  # For the highlighting of the expression

        ln = LookupNode(loc=value_range)
        ln.intelligence_node = self
        code_intel.add_lookup_node(ln)

    def hover(self):

        def _self_is_io(_path):
            if "in" in _path:
                return False

            for _component in ["secondaryFiles", "position", "valueFrom"]:
                if _component in _path:
                    return True
            else:
                return False

        def _self_is_outputEval(_path):
            return "in" not in _path and "outputEval" in _path

        def _self_is_in_step(_path):
            if "in" in _path and "valueFrom" in _path:
                return True
            else:
                return False

        job_inputs = self.execution_context.sample_data["inputs"]
        job_outputs = self.execution_context.sample_data["outputs"]
        cwl_self = None

        # Deal with filling out self
        try:
            if _self_is_io(self.intel_context.path):
                if "inputs" in self.intel_context.path:
                    cwl_self = job_inputs.get(self.intel_context.path[1])
                elif "outputs" in self.intel_context.path:
                    cwl_self = job_outputs[self.intel_context.path[1]]

            elif _self_is_outputEval(self.intel_context.path):
                # todo: Need to check for `glob`
                cwl_self = self.execution_context.get_sample_globbed_files(self.intel_context.path[1])

            elif _self_is_in_step(self.intel_context.path):
                job_inputs, cwl_self = \
                    self.execution_context.get_workflow_step_inputs(self.intel_context.path)

        except (ValueError, IndexError) as e:
            pass

        if job_inputs:
            res = "".join(
                evaluate_expression(
                    expression=fragment["exp"],
                    exp_type=fragment["type"],
                    expression_lib=self.execution_context.expression_lib,
                    runtime=self.execution_context.runtime(self.intel_context.path),
                    inputs=job_inputs,
                    cwl_self=cwl_self)
                for fragment in self._split_fragments())
        else:
            res = "Job inputs have not been filled out"

        return Hover(res, self.range)

    def definition(self):
        # Hijacking this to show the sample inputs file
        return Location(self.execution_context.get_sample_data_file_path().as_uri())

    def _split_fragments(self) -> list:
        refs = parameter_ref.finditer(self.text)
        exps = expression_ref.finditer(self.text)
        r, e = next(refs, None), next(exps, None)

        cursor = 0
        fragments = []
        while r or e:
            if r is not None and e is not None:
                if r.start() < e.start():
                    _frag = self._add_ref(r)
                    r = next(refs, None)
                else:
                    _frag = self._add_exp(e)
                    e = next(exps, None)
            else:
                if r is not None:
                    _frag = self._add_ref(r)
                    r = next(refs, None)
                elif e is not None:
                    _frag = self._add_exp(e)
                    e = next(exps, None)

            plain_string_frag = self._add_plain_string(self.text, (cursor, _frag["span"][0]))
            cursor = _frag["span"][1]
            fragments += [plain_string_frag, _frag]

        plain_string_frag = self._add_plain_string(self.text, (cursor, len(self.text)))
        fragments += [plain_string_frag]
        return fragments

    @staticmethod
    def _add_plain_string(text, span):
        return {
            "exp": text[span[0]:span[1]],
            "type": ExpressionType.PlainString,
            "span": span
        }

    @staticmethod
    def _add_ref(r):
        return {
            "exp": r.groups()[0],
            "type": ExpressionType.ParameterReference,
            "span": r.span()
        }

    @staticmethod
    def _add_exp(e):
        return {
            "exp": e.groups()[0],
            "type": ExpressionType.JSExpression,
            "span": e.span()
        }


def parameter_reference_template(expression):
    return f"""
var runtime = dukpy['runtime'];
var inputs = dukpy['inputs'];
var self = dukpy['cwl_self'];
{expression}"""


def js_template(expression):
    return f"""
var runtime = dukpy['runtime'];
var inputs = dukpy['inputs'];
var self = dukpy['cwl_self'];
function benten_eval_func() {{
    {expression} 
}};
benten_eval_func()"""


def evaluate_expression(
        expression: str, exp_type: ExpressionType,
        expression_lib: list, runtime: dict, inputs: dict, cwl_self: dict):
    if exp_type == ExpressionType.PlainString:
        return expression

    if inputs:
        if exp_type == ExpressionType.ParameterReference:
            full_expression = parameter_reference_template(expression)
        else:
            full_expression = js_template(expression)

        try:
            res = dukpy.evaljs(expression_lib + [full_expression],
                               runtime=runtime,
                               inputs=inputs,
                               cwl_self=cwl_self)

            if res is None and exp_type == ExpressionType.JSExpression:
                res = "Got a 'null' result. Do you have a `return` for your JS expression?"
            else:
                res = str(res)

        except dukpy.JSRuntimeError as e:
            res = str(e).splitlines()[0]
            logger.error(res)
    else:
        res = "Job inputs have not been filled out"

    return res
