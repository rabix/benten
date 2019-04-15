from typing import List

from .documentproblem import DocumentProblem


class Base:
    def __init__(self, ydict: (dict, str), existing_issues: List[DocumentProblem]=None):
        self.ydict = ydict
        self.problems: List[DocumentProblem] = existing_issues or []

