"""<shudder> factory </shudder> for creating a model based on inferring the process type"""
from typing import List, Tuple

from .lineloader import parse_yaml_with_line_info, YNone, Ystr, Ydict, DocumentError, LAM
from .documentproblem import DocumentProblem
from .base import Base
from .commandlinetool import CommandLineTool
from .workflow import Workflow

import logging
logger = logging.getLogger(__name__)


def infer_type(ydict: (str, dict)):
    if isinstance(ydict, dict):
        return (ydict or {}).get("class", "unknown")
    else:
        return "unknown"


# will extend to include expressions and docs
def create_model(text: str):
    yaml, problems = _parse_yaml(text)
    try:
        return {
            "unknown": Base,
            "CommandLineTool": CommandLineTool,
            "Workflow": Workflow
        }.get(infer_type(yaml), Base)(yaml, problems)
    except Exception as e:
        raise e
        # # As a last resort, we write this out. Means we haven't hardened our constructors enough
        # # Should only do this in production - this removes info useful for debugging
        # logger.error(str(e))
        # return Unk(yaml_doc)


def _parse_yaml(text) -> Tuple[dict, List[DocumentProblem]]:
    problems = []
    try:
        yaml = parse_yaml_with_line_info(
            text, convert_to_lam=True, errors=problems) or Ydict.empty()
    except DocumentError as e:
        yaml = None
        problems = [
            DocumentProblem(line=e.line, column=e.column, message=e.message,
                            problem_type=DocumentProblem.Type.error,
                            problem_class=DocumentProblem.Class.yaml)]

    return yaml, problems
