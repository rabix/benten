#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from ruamel.yaml import YAML

from benten.models.cursorcontext import node_at, Mark


current_path = pathlib.Path(__file__).parent


def load_test_yaml():
    yaml = YAML(typ="rt")
    return yaml.load(current_path / "yaml" / "sample.yaml")


def test_dict_toplevel():
    doc = load_test_yaml()

    p = node_at(doc, line=0, col=2)
    assert p.path == []
    assert p.mark == Mark.nothing

    p = node_at(doc, line=3, col=2)
    assert p.path == ['k1', 'k1']
    assert p.mark == Mark.key

    p = node_at(doc, line=3, col=9)
    assert p.path == ['k1', 'k1', 'k1']
    assert p.mark == Mark.key

    p = node_at(doc, line=18, col=0)
    assert p.path == []
    assert p.mark == Mark.nothing

    p = node_at(doc, line=18, col=2)
    assert p.path == ['k2']
    assert p.mark == Mark.nothing


def test_dict_recursive():
    doc = load_test_yaml()

    p = node_at(doc, line=15, col=2)
    assert p.path == ['k2', 'k4', 'k1']
    assert p.mark == Mark.value
