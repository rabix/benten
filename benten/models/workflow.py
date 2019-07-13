#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .intelligence import Completer


def analyze_connectivity(completer: Completer, problems: list):
    """
    - Parse the linked step processes to establish the available interfaces
    - Previously, for each step, each in and out field should have custom
      completers prepared. Fill in the data for these completers.
    - Return a workflow connectivity graph
    """

