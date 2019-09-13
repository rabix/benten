"""This keeps track of any context needed for auto-completions and expression evaluations
This therefore carries """

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from typing import List
from dataclasses import dataclass

from .intelligence import IntelligenceNode
from .workflow import Workflow, WFStepIntelligence


@dataclass
class IntelligenceContext:
    path: List[str] = None
    workflow: Workflow = None
    workflow_step_intelligence: WFStepIntelligence = None
    requirements: IntelligenceNode = None


def copy_context(old: IntelligenceContext) -> IntelligenceContext:
    return IntelligenceContext(
        path=list(old.path),
        workflow=old.workflow,
        workflow_step_intelligence=old.workflow_step_intelligence,
        requirements=old.requirements)
