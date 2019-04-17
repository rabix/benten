from .process import Process


class CommandLineTool(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        fields = {
            "class": True,
            "cwlVersion": True,
            "id": False,
            "doc": False,
            "label": False,
            "inputs": True,
            "outputs": True,
            "baseCommand": False,
            "requirements": False,
            "hints": False
        }
        self.parse_sections(fields)
