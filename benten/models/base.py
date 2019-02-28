from ..editing.cwldoc import CwlDoc


class Base:
    """We don't know what the user intends this to be"""

    def __init__(self, cwl_doc: CwlDoc):
        self.cwl_doc = cwl_doc or {}
        self.id = (self.cwl_doc.cwl_dict or {}).get("id", None)
        self.section_lines = {}
        self.cwl_errors = []

    @staticmethod
    def special_id(name):
        """We distinguish this from a step id and try and avoid name clashes"""
        return "- {} -".format(name)

    def parse_sections(self, required_sections: list):
        cwl_dict = self.cwl_doc.cwl_dict

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
                self.cwl_errors += ["'{}' missing".format(missing_section)]


# Some patterns we use a lot
special_id_for_inputs = Base.special_id("inputs")
special_id_for_outputs = Base.special_id("outputs")
special_ids_for_io = [special_id_for_inputs, special_id_for_outputs]
