from .base import Base, YamlView


class Tool(Base):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        required_sections = ["cwlVersion", "class", "inputs", "outputs", "steps"]
        self.parse_sections(required_sections)
