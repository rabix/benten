"""Contains methods to use the line/column information in the
keys and values in the loaded YAML.

We need to indicate the start and end locations of keys/values
for diagnostics and symbols (document structure)

Given a cursor location we need to retrieve the document element
it covers.
"""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from typing import Union
from enum import IntEnum

from ruamel.yaml.comments import CommentedMap, CommentedSeq


class Mark(IntEnum):
    nothing = 0
    key = 1
    value = 2


def range_for(node: Union[CommentedMap, CommentedSeq],
              key_or_index: Union[str, int] = None,
              mark: Mark = None):
    if key_or_index is None:
        start = (node.lc.line, node.lc.col)
        _l = 1

    else:
        mark = mark or Mark.value

        if mark == Mark.key:
            start = node.lc.key(key_or_index)
            _l = len(key_or_index)
        else:
            start = node.lc.value(key_or_index) if isinstance(node, CommentedMap) \
                else node.lc.item(key_or_index)
            v = node[key_or_index]
            if isinstance(v, (str, int, float)):
                _l = len(str(v))
            else:
                _l = 1  # Need a better way to figure out blocks.

    end = (start[0], start[1] + _l)
    return start, end


class CursorPath:

    def __init__(self, path: list, mark: Mark):
        self.path = path
        self.mark = mark


def node_at(doc: Union[CommentedMap, CommentedSeq], line: int, col: int,
            p: list=None):
    if p is None:
        p = []

    if isinstance(doc, CommentedMap):
        return dict_node_at(doc, line, col, p)
    elif isinstance(doc, CommentedSeq):
        return list_node_at(doc, line, col, p)
    else:
        return None


def dict_node_at(doc: CommentedMap, line: int, col: int, p: list):
    last_key = None
    this_indent = None

    for k in doc.keys():
        l, c = doc.lc.key(k)
        this_indent = c

        if col < c:
            return None

        if line < l:
            if last_key is None:
                return CursorPath(p, Mark.nothing)
            else:
                return node_at(doc[last_key], line, col, p + [last_key])

        if line == l:
            if col < c + len(k):
                return CursorPath(p + [k], Mark.key)

            else:
                vl, vc = doc.lc.value(k)
                if col < vc:
                    return CursorPath(p + [k], Mark.value)

        last_key = k

    else:

        # The two ways we get here is
        # a) when our cursor is at or past the last key
        # b) the node was empty to start with

        # When it is within the last key (which is obviously not a single value
        # given that it was not captured by the line == l condition above)
        # it's business as usual - we recurse into the node we just passed by.

        # When it is past the last key we recurse down to the last value, which
        # is a scalar. At this point we have to come back out. The path we report
        # back depends on the indentation we have

        if last_key is not None:
            cp = node_at(doc[last_key], line, col, p + [last_key])
            if cp is None:
                # OK. Time to come back out and report a path based on indentation
                if col == this_indent:
                    return CursorPath(p, Mark.nothing)
                else:
                    return None
            else:
                # This is a proper path
                return cp

        else:
            # Node was empty
            return CursorPath(p, Mark.nothing)


def list_node_at(doc: CommentedSeq, line: int, col: int, p: list):
    pass


#
# def search_list(line, column, node, path):
#     l = len(node)
#     if line < node.lc.line:
#         return None
#
#     for i in range(1, l):
#         if line < node.lc.item(i):
#             v = node[i - 1]
#             if isinstance(v, list):
#                 return search_list(line, column, v, path + [i])
#             elif isinstance(v, dict):
#                 return search_dict(line, column, v, path + [i])
#             else:
#                 return path
#     else:
#         pass
#
#     return None


# def search_dict(line, column, node, path):
#     if line < node.lc.line:
#         return None
#
#     for k, v in


# def compute_path(
#         doc: Union[Ydict, Ylist], line, column,
#         path: Tuple[Union[str, int], ...] = (),
#         indent=0) -> Union[None, Tuple[Union[str, int], ...]]:
#     if not isinstance(doc, (dict, list)):  # Leaf node
#         return path
#
#     values = doc.items() if isinstance(doc, dict) else enumerate(doc)
#     new_path = None
#     for k, v in values:
#         try:
#             if line < v.start.line:
#                 continue
#             if line > v.end.line:
#                 continue
#             if v.start.line == line and column < v.start.column:
#                 continue
#             if v.end.line == line and column >= v.end.column:
#                 continue
#
#             new_path = compute_path(v, line, column, path + (k,), v.start.column)
#             break
#         except AttributeError:
#             pass
#
#     if new_path is None:
#         if column >= indent:
#             return path
#         else:
#             return None
#     else:
#         return new_path
#
