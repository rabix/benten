"""A small class handling instructions on what kind of edits to do to a document"""

from typing import List, Union

from .lineloader import Ydict, Ylist


class EditMark:
    def __init__(self, line, column):
        self.line, self.column = line, column


class Edit:
    def __init__(self, start, end, text):
        self.start, self.end, self.text = start, end, text


def find_section(parent: (Ydict, Ylist), keys: List[Union[int, str]]):
    if len(keys) > 1:
        return find_section(parent[keys[0]], keys[1:])
    else:
        return parent[keys]

def get_lines(node: (Ydict, Ylist), lines: List[str]):
    pass






def add_item_to_map(lines: List[str], existing_map: Ydict, new_value: str):
    """Find the last item of this map and place the new_value there"""
    *_, last_key = existing_map.keys()
    st_ln = existing_map[last_key].end_mark.line
