from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity, Range, Position
from .base import Base


class Process(Base):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outline_info = {}

    def parse_sections(self, fields):
        for k, v in self.ydict.items():
            self.outline_info[k] = {"range": (v.start, v.end)}

        for k in self.outline_info.keys():
            if k not in fields:
                self.problems += [
                    Diagnostic(
                        _range=Range(
                            start=Position(self.ydict[k].start.line, 0),
                            end=Position(self.ydict[k].end.line, self.ydict[k].end.column)),
                        message=f"Illegal section: {k}",
                        severity=DiagnosticSeverity.Error,
                        code="CWL err",
                        source="Benten")]

        for k, _required in fields.items():
            if _required:
                if k not in self.outline_info:
                    self.problems += [
                        Diagnostic(
                            _range=Range(start=Position(0, 0), end=Position(0, 1)),
                            message=f"Missing required section: {k}",
                            severity=DiagnosticSeverity.Error,
                            code="CWL err",
                            source="Benten")]
