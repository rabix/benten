#  Copyright (c) 2019 Seven Bridges. See LICENSE

import time
from typing import Tuple, List

from ruamel.yaml import YAML
from ruamel.yaml.parser import ParserError
from ruamel.yaml.scanner import ScannerError

from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity, Range, Position
from .languagemodel import parse_document


import logging
logger = logging.getLogger(__name__)

yaml_parser = YAML(typ="rt")
# TODO: allow checking for duplicate keys, perhaps with self healing
yaml_parser.allow_duplicate_keys = True


def _parse_yaml(text, retries=3) -> Tuple[dict, List[Diagnostic]]:
    problems = []
    try:
        cwl = yaml_parser.load(text)
    except (ParserError, ScannerError) as e:

        if retries:

            # TODO: refactor - cleanup healing code
            if e.problem == "could not find expected ':'":
                return _parse_yaml(heal_incomplete_key(text, e), retries - 1)

            if e.problem == "mapping values are not allowed here":
                return _parse_yaml(heal_incomplete_key_typeB(text, e), retries - 1)

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
    lines = original_text.splitlines(keepends=False)
    # TODO: This only works for block style, but it does the job
    lines[e.context_mark.line] = lines[e.context_mark.line] + ":"
    return "\n".join(lines)


def heal_incomplete_key_typeB(original_text, e):
    logger.debug("Healing type B!")
    lines = original_text.splitlines(keepends=False)
    # Walk back up to first non-empty line and slap a ":" on the end
    ln = e.problem_mark.line - 1
    while ln > 0 and len(lines[ln].strip()) == 0:
        ln -= 1

    if len(lines[ln]):
        lines[ln] = lines[ln] + ":"

    return "\n".join(lines)


class Document:

    def __init__(self,
                 doc_uri: str,
                 text: str,
                 version: int,
                 language_models: dict):
        self.doc_uri = doc_uri
        self.text = text
        self.version = version
        self.language_models = language_models

        self.problems = None
        self.completer = None
        self.symbols = None

        self.update(text)

    def update(self, new_text):
        self.text = new_text

        t0 = time.time()
        cwl, problems = _parse_yaml(self.text)
        t1 = time.time()
        self.completer, self.symbols, self.problems = \
            parse_document(cwl, self.doc_uri, self.text, self.language_models, problems)
        t2 = time.time()
        logger.debug(f"Took {t1 - t0:1.3}s to load document")
        logger.debug(f"Took {t2 - t1:1.3}s to parse document")

    def definition(self, loc: Position):
        de = self.completer.get_doc_element(loc)
        if de is not None:
            return de.definition()

    def completion(self, loc: Position, dummy):
        de = self.completer.get_doc_element(loc)
        if de is not None:
            return de.completion()

    def hover(self, loc: Position):
        pass