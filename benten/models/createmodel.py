"""<shudder> factory </shudder> for creating a model based on inferring the process type"""
from ..editing.yamldoc import YamlDoc
from .unk import Unk
from .commandlinetool import CommandLineTool
from .workflow import Workflow

import logging
logger = logging.getLogger(__name__)


def infer_type(yaml_doc: YamlDoc):
    return (yaml_doc.yaml or {}).get("class", "unknown")


def create_model(yaml_doc: YamlDoc):
    try:
        return {
            "unknown": Unk,
            "CommandLineTool": CommandLineTool,
            "Workflow": Workflow
        }.get(infer_type(yaml_doc), Unk)(yaml_doc)
    except Exception as e:
        raise e
        # # As a last resort, we write this out. Means we haven't hardened our constructors enough
        # # Should only do this in production - this removes info useful for debugging
        # logger.error(str(e))
        # return Unk(yaml_doc)
