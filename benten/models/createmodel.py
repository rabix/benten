"""<shudder> factory </shudder> for creating a model based on inferring the process type"""
from typing import List

from ..editing.documentproblem import DocumentProblem
from .unk import Unk
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
def create_model(ydict: (str, dict), existing_issues: List[DocumentProblem]=None):
    try:
        # return {
        #     "unknown": Unk,
        #     "CommandLineTool": CommandLineTool,
        #     "Workflow": Workflow
        # }.get(infer_type(ydict), Unk)(ydict, existing_issues)
        return Unk(ydict, existing_issues)
    except Exception as e:
        raise e
        # # As a last resort, we write this out. Means we haven't hardened our constructors enough
        # # Should only do this in production - this removes info useful for debugging
        # logger.error(str(e))
        # return Unk(yaml_doc)
