"""Load the raw YAML"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from typing import Tuple, List

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError
from ruamel.yaml.composer import ComposerError
from ruamel.yaml.compat import StringIO

from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity, Range, Position


import logging
logger = logging.getLogger(__name__)

_yaml_loader = YAML(typ="rt")
# TODO: allow checking for duplicate keys, perhaps with self healing
_yaml_loader.allow_duplicate_keys = True

fast_load = YAML(typ='safe')
fast_load.indent(mapping=2, sequence=4, offset=2)
fast_load.default_flow_style = False


def fast_yaml_load(txt):
    try:
        return fast_load.load(txt)
    except (ParserError, ScannerError) as e:
        pass


def yaml_to_string(v: dict):
    s = StringIO()
    fast_load.dump(v, s)
    return s.getvalue()


def parse_yaml(text, retries=3) -> Tuple[dict, List[Diagnostic]]:
    problems = []
    try:
        cwl = _yaml_loader.load(text)
    except (ParserError, ScannerError, ComposerError) as e:

        if retries:

            # TODO: refactor - cleanup healing code
            if e.problem == "could not find expected ':'":
                return parse_yaml(heal_incomplete_key(text, e), retries - 1)

            if e.problem == "mapping values are not allowed here":
                return parse_yaml(heal_incomplete_key_typeB(text, e), retries - 1)

        cwl = None
        problems = [
            Diagnostic(
                _range=Range(start=Position(e.problem_mark.line, e.problem_mark.column),
                             end=Position(e.problem_mark.line, e.problem_mark.column)),
                message=str(e),
                severity=DiagnosticSeverity.Error,
                code="YAML err",
                source="Benten")]

    return cwl, problems


def heal_incomplete_key(original_text, e):
    logger.debug("Attempting to heal incomplete key")
    lines = original_text.splitlines(keepends=False)
    # TODO: This only works for block style, but it does the job
    lines[e.context_mark.line] = lines[e.context_mark.line] + ":"
    return "\n".join(lines)


def heal_incomplete_key_typeB(original_text, e):
    logger.debug("Attempting to heal incomplete key")
    lines = original_text.splitlines(keepends=False)
    # Walk back up to first non-empty line and slap a ":" on the end
    ln = e.problem_mark.line - 1
    while ln > 0 and len(lines[ln].strip()) == 0:
        ln -= 1

    if len(lines[ln]):
        lines[ln] = lines[ln] + ":"

    return "\n".join(lines)
