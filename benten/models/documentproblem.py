from enum import Enum


class DocumentProblem:
    class Class(Enum):
        yaml = 0
        cwl = 1

    class Type(Enum):
        error = 0
        warning = 1
        information = 2

    def __init__(
            self, line: int, column: int, message: str,
            problem_type: 'DocumentProblem.Type', problem_class: 'DocumentProblem.Class'):
        self.line = line
        self.column = column
        self.message = message
        self.problem_type = problem_type
        self.problem_class = problem_class
