from ..editing.lineloader import reverse_lookup
from .base import Base


class CommandLineTool(Base):

    autocomplete_dict = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = (self.cwl_doc.yaml or {}).get("id", None)

        required_sections = ["cwlVersion", "class", "inputs", "outputs", "steps"]
        self.parse_sections(required_sections)

    def get_auto_completions(self, line, column, prefix):
        completions = [
            {
                "caption": "Docker",
                #"name": "Example",
                #"value": "Hello!",
                "snippet": "Black velvet and that little boy smile\nBlack velvet and that slow southern style",
                # "score": 10,
                # "meta": "snippet"
            }
        ]

        if self.cwl_doc.yaml is not None:
            inline_path, val = reverse_lookup(line, column, self.cwl_doc.yaml)

        return completions
