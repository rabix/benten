from typing import List
import yaml

from ..configuration import Configuration
from .documentproblem import DocumentProblem
from .base import Base


class Process(Base):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.section_lines = {}
