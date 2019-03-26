from typing import List

from ..editing.edit import EditMark
from ..editing.yamlview import YamlView


class CWLError:
    def __init__(self, pos: EditMark, message: str):
        self.pos = pos
        self.message = message


class Base:
    """We don't know what the user intends this to be"""

    autocomplete_dict = {}

    def __init__(self, cwl_doc: YamlView):
        self.cwl_doc = cwl_doc
        self._original_raw_cwl = cwl_doc.raw_text
        self.section_lines = {}
        self.cwl_errors: List[CWLError] = []

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
                    CWLError(EditMark(), "'{}' missing".format(missing_section))]

    def get_auto_completions(self, line, column, prefix):
        return []
        # return [
        #     {
        #         "caption": "example",
        #         "name": "Example",
        #         "value": "value" + prefix,
        #         "snippet": "My my\nwhat a beautiful sky",
        #         "score": 10,
        #         "meta": "Metadata"
        #     }
        # ]

# Some patterns we use a lot
special_id_for_inputs = Base.special_id("inputs")
special_id_for_outputs = Base.special_id("outputs")
special_ids_for_io = [special_id_for_inputs, special_id_for_outputs]
