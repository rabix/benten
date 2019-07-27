#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib
import urllib.parse

from ..langserver.lspobjects import Diagnostic, DiagnosticSeverity, Range, Position


def get_range_for_key(parent, key):
    start = parent.lc.key(key)
    end = (start[0], start[1] + len(key))
    return Range(Position(*start), Position(*end))


# TODO: refactor this for redundancy
def get_range_for_value(node, key):
    if isinstance(node, dict):
        start = node.lc.value(key)
    else:
        start = node.lc.item(key)

    v = node[key]
    if v is None:
        v = ""
    else:
        v = str(v)  # How to handle multi line strings

    end = (start[0], start[1] + len(v))
    return Range(Position(*start), Position(*end))


class ListOrMap:

    def __init__(self, node, key_field, problems):
        self.was_dict = None
        self.node = {}
        self.key_ids = {}
        if isinstance(node, dict):
            self.node = node
            self.was_dict = True
        elif isinstance(node, list):
            for n, _item in enumerate(node):
                if isinstance(_item, dict):
                    key = _item.get(key_field)
                    if key is not None:
                        self.node[key] = _item
                        self.key_ids[key] = get_range_for_value(_item, key_field)
                    else:
                        problems += [
                            Diagnostic(
                                _range=get_range_for_value(node, n),
                                message=f"Missing key field {key_field}",
                                severity=DiagnosticSeverity.Error)
                        ]

    def get_range_for_id(self, key):
        if self.was_dict:
            return get_range_for_key(self.node, key)
        else:
            return self.key_ids[key]

    def get_range_for_value(self, key):
        return get_range_for_value(self.node, key)


# TODO: Deprecate this function
def list_as_map(node, key_field, problems):
    if isinstance(node, dict):
        return node

    new_node = {}

    if isinstance(node, list):
        for n, _item in enumerate(node):
            if isinstance(_item, dict):
                key = _item.get(key_field)
                if key is not None:
                    new_node[key] = _item
                else:
                    problems += [
                        Diagnostic(
                            _range=get_range_for_value(node, n),
                            message=f"Missing key field {key_field}",
                            severity=DiagnosticSeverity.Error)
                    ]

    return new_node


def check_linked_file(doc_uri: str, path: str, loc: Range, problems: list):
    linked_file = resolve_file_path(doc_uri, path)
    if not linked_file.exists():
        problems += [
            Diagnostic(
                _range=loc,
                message=f"Missing document: {path}",
                severity=DiagnosticSeverity.Error)
        ]
        return
    elif not linked_file.is_file():
        problems += [
            Diagnostic(
                _range=loc,
                message=f"Linked document must be file: {path}",
                severity=DiagnosticSeverity.Error)
        ]
        return
    else:
        return linked_file


def resolve_file_path(doc_uri, target_path):
    _path = pathlib.PurePosixPath(target_path)
    if not _path.is_absolute():
        base_path = pathlib.Path(urllib.parse.urlparse(doc_uri).path).parent
    else:
        base_path = "."
    _path = pathlib.Path(base_path / _path).resolve().absolute()
    return _path
