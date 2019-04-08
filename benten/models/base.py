from typing import List
import yaml

from ..configuration import Configuration
from ..editing.documentproblem import DocumentProblem
from ..editing.edit import EditMark
from ..editing.yamlview import YamlView


class Base:
    """We don't know what the user intends this to be"""

    _auto_complete_snippets = {}

    def __init__(self, cwl_doc: YamlView):
        self.cwl_doc = cwl_doc
        self._original_raw_cwl = cwl_doc.raw_text
        self.section_lines = {}
        self.cwl_errors: List[DocumentProblem] = []

    def code_is_same_as(self, new_text):
        return self._original_raw_cwl == new_text

    @staticmethod
    def special_id(name):
        """We distinguish this from a step id and try and avoid name clashes"""
        return "- {} -".format(name)

    def parse_sections(self, required_sections: list):
        cwl_dict = self.cwl_doc.yaml

        for section, doc in cwl_dict.items():
            if section in required_sections:
                required_sections.remove(section)
            try:
                self.section_lines[Base.special_id(section)] = \
                    (cwl_dict[section].start, cwl_dict[section].end)
            # todo: enhance YAML loader to construct ints, floats etc.
            except AttributeError:
                pass

        if len(required_sections):
            for missing_section in required_sections:
                self.cwl_errors += [
                    DocumentProblem(line=0, column=0, message="'{}' missing".format(missing_section),
                                    problem_type=DocumentProblem.Type.warning,
                                    problem_class=DocumentProblem.Class.cwl)]

    def get_auto_completions(self, line, column, prefix):
        if len(self.cwl_doc.raw_lines) > 1:
            return []
        else:
            return [
                self._auto_complete_snippets[k]
                for k in ["CommandLineTool", "ExpressionTool", "Workflow"]
            ]

    @staticmethod
    def prepare_auto_completions(config: Configuration):

        try:
            raw_snippets = yaml.load(
                config.getpath("editor", "snippets_file").open("r").read())
        except FileNotFoundError as e:
            Warning("Could not find snippets file. No auto completions available")
            return

        for k, v in raw_snippets.items():
            v["caption"] = k
            v["snippet"] = v.get("snippet", k)
            Base._auto_complete_snippets[k] = v

        # The fields ACE expects
        # {
        #     "caption": snip.get("name", "Unknown"),
        #     # "name": "Example",
        #     # "value": "value" + prefix,
        #     "snippet": snip.get("content", None),
        #     "score": 10,
        #     "meta": snip.get("meta", "snippet")
        # }


# Some patterns we use a lot
special_id_for_inputs = Base.special_id("inputs")
special_id_for_outputs = Base.special_id("outputs")
special_ids_for_io = [special_id_for_inputs, special_id_for_outputs]
