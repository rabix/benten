"""<shudder> factory </shudder> for creating a model based on inferring the process type"""
from ..configuration import Configuration
from ..editing.yamlview import YamlView
from .unk import Unk
from .commandlinetool import CommandLineTool
from .workflow import Workflow

import logging
logger = logging.getLogger(__name__)


def infer_type(yaml_doc: YamlView):
    if isinstance(yaml_doc.yaml, dict):
        return (yaml_doc.yaml or {}).get("class", "unknown")
    else:
        return "unknown"


# will extend to include expressions and docs
def create_model(yaml_doc: YamlView, config: Configuration):
    try:
        return {
            "unknown": Unk,
            "CommandLineTool": CommandLineTool,
            "Workflow": Workflow
        }.get(infer_type(yaml_doc), Unk)(yaml_doc, config=config)
    except Exception as e:
        raise e
        # # As a last resort, we write this out. Means we haven't hardened our constructors enough
        # # Should only do this in production - this removes info useful for debugging
        # logger.error(str(e))
        # return Unk(yaml_doc)
