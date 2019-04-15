import pathlib

from ..implementationerror import ImplementationError
from .documentproblem import DocumentProblem
from .lineloader import parse_yaml_with_line_info, YNone, Ystr, Ydict, DocumentError, LAM
from .createmodel import create_model


class Document:

    def __init__(self,
                 base_path: pathlib.Path,
                 text: str,
                 version: int):
        self.base_path = base_path
        self.text = text
        self.version = version

        self.model = None
        self._last_good_model = None

        self._parse_model()

    def _parse_model(self):
        self.model = create_model(self.text)
