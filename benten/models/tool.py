from .base import Base, YamlDoc


class Tool(Base):

    def __init__(self, cwl_doc: YamlDoc):
        super().__init__(cwl_doc=cwl_doc)

        required_sections = ["cwlVersion", "class", "inputs", "outputs", "steps"]
        self.parse_sections(required_sections)
