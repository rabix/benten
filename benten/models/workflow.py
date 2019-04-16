from .process import Process


class Workflow(Process):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_sections = ["cwlVersion", "class", "inputs", "outputs"]
        self.parse_sections(required_sections)
