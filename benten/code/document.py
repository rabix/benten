#  Copyright (c) 2019 Seven Bridges. See LICENSE

import time
import pathlib

from .yaml import parse_yaml
from .intelligence import Intelligence
from .intelligencecontext import IntelligenceContext
from ..cwl.specification import latest_published_cwl_version, process_types
from ..cwl.typeinference import infer_type
from .symbols import extract_symbols, extract_step_symbols
from ..langserver.lspobjects import Position

import logging
logger = logging.getLogger(__name__)


class Document:

    def __init__(self,
                 doc_uri: str,
                 scratch_path: pathlib.Path,  # Needed for ExecutionContext's example input file
                 text: str,
                 version: int,
                 type_dicts: dict):
        self.doc_uri = doc_uri
        self.config = scratch_path
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
        self.symbols = []

        t0 = time.time()
        cwl, self.problems = parse_yaml(self.text)
        t1 = time.time()
        logger.debug(f"Took {t1 - t0:1.3}s to load document")

        if not isinstance(cwl, dict):
            return

        t2 = time.time()
        self.code_intelligence.load_namespaces(cwl)
        self.code_intelligence.prepare_execution_context(self.doc_uri, cwl, self.config)

        self.parse(cwl)
        t3 = time.time()
        logger.debug(f"Took {t3 - t2:1.3}s to parse document")

        self.symbology(cwl)

    def definition(self, loc: Position):
        de = self.code_intelligence.get_doc_element(loc)
        if de is not None:
            return de.definition()

    def completion(self, loc: Position):
        de = self.code_intelligence.get_doc_element(loc)
        if de is not None:
            return de.completion()

    def hover(self, loc: Position):
        de = self.code_intelligence.get_doc_element(loc)
        if de is not None:
            return de.hover()

    def parse(self, cwl):
        cwl_v = cwl.get("cwlVersion")
        if cwl_v not in self.type_dicts:
            logger.error(f"No language model for cwl version {str(cwl_v)}. "
                         f"Using {latest_published_cwl_version}")
            cwl_v = latest_published_cwl_version

        lm = self.type_dicts.get(cwl_v)
        inferred_type = infer_type(
            node=cwl,
            allowed_types=[lm.get(t) for t in process_types])
        inferred_type.parse(
            doc_uri=self.doc_uri,
            node=cwl,
            intel_context=IntelligenceContext(path=[]),
            code_intel=self.code_intelligence,
            problems=self.problems)

    def symbology(self, cwl):
        line_count = self.text.count("\n")

        symbols = {}
        _typ = cwl.get("class")
        if _typ in process_types:
            symbols = extract_symbols(cwl, line_count)

            if _typ == "Workflow":
                symbols = extract_step_symbols(cwl, symbols)

        self.symbols = list(symbols.values())

    def graphology(self, cwl):
        pass
        # _typ = cwl.get("class")
        # if _typ == "Workflow":
        #     self.wf_graph = analyze_connectivity(completer, self.problems)
