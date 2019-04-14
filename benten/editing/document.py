import pathlib

from ..implementationerror import ImplementationError
from .documentproblem import DocumentProblem
from .lineloader import parse_yaml_with_line_info, YNone, Ystr, Ydict, DocumentError, LAM
from ..models.createmodel import create_model


class Document:

    def __init__(self,
                 base_path: pathlib.Path,
                 text: str,
                 version: int):
        self.base_path = base_path
        self.text = text
        self.version = version
        self._last_good_yaml = None
        self.yaml = None
        self.yaml_error = []
        self.model = None
        self.cwl_problems = []

        self._process()

    def did_change(self, params):
        pass

    def auto_complete(self, params):
        return self.model.get_auto_completions(params)

    def _process(self):
        self._parse_yaml()
        self._parse_model()

    def _parse_yaml(self):
        try:
            self.yaml = parse_yaml_with_line_info(
                self.text, convert_to_lam=True, errors=self.cwl_problems) or Ydict.empty()
            self.yaml_error = []
            self._last_good_yaml = self.yaml
        except DocumentError as e:
            self.yaml = None
            self.yaml_error = [
                DocumentProblem(line=e.line, column=e.column, message=e.message,
                                problem_type=DocumentProblem.Type.error,
                                problem_class=DocumentProblem.Class.yaml)]

    def _parse_model(self):
        # todo: error catching
        self.model = create_model(self.yaml, self.yaml_error + self.cwl_problems)
