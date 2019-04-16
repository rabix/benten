"""<shudder> factory </shudder> for creating a model based on inferring the process type"""
from typing import List, Tuple

from .lineloader import parse_yaml_with_line_info, YNone, Ystr, Ydict, DocumentError, LAM
from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity, Range, Position
from .base import Base
from .undefined import Undefined
from .plaintext import PlainText
from .commandlinetool import CommandLineTool
from .workflow import Workflow

import logging
logger = logging.getLogger(__name__)


def infer_type(ydict: (None, str, dict)):
    if ydict is None:
        return "undefined"
    elif isinstance(ydict, str):
        return "text"
    elif isinstance(ydict, dict):
        return (ydict or {}).get("class", "unknown")
    else:
        return "unknown"


# will extend to include expressions and docs
def create_model(text: str):
    yaml, problems = _parse_yaml(text)
    try:
        return {
            "undefined": Undefined,
            "text": PlainText,
            "unknown": Base,
            "CommandLineTool": CommandLineTool,
            "Workflow": Workflow
        }.get(infer_type(yaml), PlainText)(yaml, problems)
    except Exception as e:
        raise e
        # # As a last resort, we write this out. Means we haven't hardened our constructors enough
        # # Should only do this in production - this removes info useful for debugging
        # logger.error(str(e))
        # return Unk(yaml_doc)


def _parse_yaml(text) -> Tuple[dict, List[Diagnostic]]:
    problems = []
    try:
        yaml = parse_yaml_with_line_info(
            text, convert_to_lam=True, errors=problems) or Ydict.empty()
    except DocumentError as e:
        yaml = None
        problems = [
            Diagnostic(
                _range=Range(start=Position(e.line, e.column), end=Position(e.line, e.column)),
                message=e.message,
                severity=DiagnosticSeverity.Error,
                code="YAML err",
                source="Benten")]

    return yaml, problems
