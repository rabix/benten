#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
from dataclasses import dataclass

from ruamel.yaml import YAML

from .intelligence import Completer


# TODO: Use typed objects for ports to check types
@dataclass
class StepInterface:
    inputs: set
    outputs: set


def parse_interface(file_path: pathlib.Path):
    pass


def analyze_connectivity(completer: Completer, problems: list):
    """
    - Parse the linked step processes to establish the available interfaces
    - Previously, for each step, each in and out field should have custom
      completers prepared. Fill in the data for these completers.
    - Return a workflow connectivity graph
    """

