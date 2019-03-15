"""<shudder> factory </shudder> for creating a model based on inferring the process type"""
from ..editing.yamldoc import YamlDoc
from .unk import Unk
from .commandlinetool import CommandLineTool
from .workflow import Workflow


def infer_type(yaml_doc: YamlDoc):
    return yaml_doc.yaml.get("class", "unknown")


def create_model(yaml_doc: YamlDoc):
    return {
        "unknown": Unk,
        "CommandLineTool": CommandLineTool,
        "Workflow": Workflow
    }.get(infer_type(yaml_doc), Unk)(yaml_doc)
