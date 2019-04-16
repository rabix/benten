from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity, Range, Position
from .base import Base


class Process(Base):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = {}

    def parse_sections(self, required_sections):
        for k, v in self.ydict.items():
            self.sections[k] = v.start, v.end

        for k in required_sections:
            if k not in self.sections:
                self.problems += [
                    Diagnostic(
                        _range=Range(start=Position(0, 0), end=Position(0, 1)),
                        message=f"Missing required section: {k}",
                        severity=DiagnosticSeverity.Error,
                        code="CWL err",
                        source="Benten")]
