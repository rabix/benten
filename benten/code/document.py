#  Copyright (c) 2019 Seven Bridges. See LICENSE

import time

from .yaml import parse_yaml
from .intelligence import Intelligence
from ..cwl.specification import latest_published_cwl_version, process_types
from .symbols import extract_symbols, extract_step_symbols

from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity, Range, Position
from .languagemodel import parse_document


import logging
logger = logging.getLogger(__name__)


class Document:

    def __init__(self,
                 doc_uri: str,
                 text: str,
                 version: int,
                 type_dicts: dict):
        self.doc_uri = doc_uri
        self.text = text
        self.version = version
        self.type_dicts = type_dicts

        self.problems = None
        self.code_intelligence = None
        self.symbols = None
        self.wf_graph = None

        self.update(text)

    def update(self, new_text):
        self.text = new_text
        self.code_intelligence = Intelligence()
        self.symbols = {}

        t0 = time.time()
        cwl, problems = parse_yaml(self.text)
        t1 = time.time()
        logger.debug(f"Took {t1 - t0:1.3}s to load document")

        if not isinstance(cwl, dict):
            return

        self.parse(cwl)
        t2 = time.time()
        logger.debug(f"Took {t2 - t1:1.3}s to parse document")

        self.symbology(cwl)


    def definition(self, loc: Position):
        de = self.code_intelligence.get_doc_element(loc)
        if de is not None:
            return de.definition()

    def completion(self, loc: Position, dummy):
        de = self.code_intelligence.get_doc_element(loc)
        if de is not None:
            return de.completion()

    def hover(self, loc: Position):
        pass

    def parse(self, cwl):
        cwl_v = cwl.get("cwlVersion")
        if cwl_v not in self.type_dicts:
            logger.error(f"No language model for cwl version {str(cwl_v)}. "
                         f"Using {latest_published_cwl_version}")
            cwl_v = latest_published_cwl_version

        lm = self.type_dicts.get(cwl_v)




        _typ = cwl.get("class")
        if _typ is not None:
            base_type = lm.get(_typ)
            value_lookup_node = ValueLookup(Range(Position(0, 0), Position(0, 0)))
            if base_type is not None:
                base_type.parse(
                    doc_uri=doc_uri,
                    node=cwl,
                    value_lookup_node=value_lookup_node,
                    lom_key=None,
                    parent_completer_node=None,
                    completer=completer,
                    problems=problems,
                    requirements=None)



    def symbology(self, cwl):
        line_count = self.text.count("\n")

        _typ = cwl.get("class")
        if _typ in process_types:
            self.symbols = extract_symbols(cwl, line_count)

            if _typ == "Workflow":
                self.symbols = extract_step_symbols(cwl, self.symbols)
                wf_graph = workflow.analyze_connectivity(completer, problems)

    def graphology(self, cwl):
        _typ = cwl.get("class")
        if _typ == "Workflow":
            self.wf_graph = analyze_connectivity(completer, self.problems)
