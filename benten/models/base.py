from ..editing.cwldoc import CwlDoc


class Base:
    """We don't know what the user intends this to be"""

    def __init__(self, cwl_doc: CwlDoc):
        self.cwl_doc = cwl_doc or {}
        self.id = self.cwl_doc.cwl_dict.get("id", None)
        self.section_lines = {}
        self.errors = []

    @staticmethod
    def res_id(name):
        return "- {} -".format(name)

    def parse_sections(self, required_sections: list):
        cwl_dict = self.cwl_doc.cwl_dict

        for section, doc in cwl_dict.items():
            if section in required_sections:
                required_sections.remove(section)
            try:
                self.section_lines[Base.res_id(section)] = \
                    (cwl_dict[section].start, cwl_dict[section].end)
            # todo: enhance YAML loader to construct ints, floats etc.
            except AttributeError:
                pass

        if len(required_sections):
            for missing_section in required_sections:
                self.errors += ["'{}' missing".format(missing_section)]
