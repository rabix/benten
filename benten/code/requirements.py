#  Copyright (c) 2019 Seven Bridges. See LICENSE

from .intelligence import IntelligenceNode
from .intelligencecontext import IntelligenceContext


class Requirements(IntelligenceContext):

    def __init__(self, req_types):
        self.req_types = req_types

    def get_completer(self):
        return IntelligenceNode(completions=self.req_types)
