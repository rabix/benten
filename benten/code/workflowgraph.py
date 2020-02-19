"""Parse CWL and create a JSON file describing the workflow. This dictionary
is directly suitable for display by vis.js, but can be parsed for any other
purpose."""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from ..cwl.lib import (ListOrMap, normalize_source)


def cwl_graph(cwl: dict):

    graph = {
        "nodes": [],
        "edges": [],
        "line-numbers": {}
    }

    inputs = ListOrMap(cwl.get("inputs", {}), key_field="id", problems=[])
    _add_nodes(graph, inputs, "inputs")

    steps = ListOrMap(cwl.get("steps", {}), key_field="id", problems=[])
    _add_nodes(graph, steps, "steps")

    outputs = ListOrMap(cwl.get("outputs", {}), key_field="id", problems=[])
    _add_nodes(graph, outputs, "outputs")

    _add_edges(graph, inputs, outputs, steps)

    return graph


def _add_nodes(graph, grp, grp_id):
    for k, v in grp.as_dict.items():
        graph["nodes"] += [{
            "id": k,
            "label": v.get("label", k) if isinstance(v, dict) else k,
            "group": grp_id
        }]
        _mark_step_modifiers(graph["nodes"][-1], v)
        graph["line-numbers"][k] = grp.get_range_for_value(k).start.line


def _mark_step_modifiers(node_data, node):
    if not isinstance(node, dict):
        return

    code, title = "", []
    _scatter = node.get("scatter")
    _conditional = node.get("when")
    if _scatter:
        code += "S"
        title += [f"Scatter on {_scatter}"]
    if _conditional:
        code += "?"
        title += [f"Conditional on {_conditional}"]
    if code:
        node_data["icon"] = {
            "code": code,
            "color": "#ffffff"
        }
    if title:
        node_data["title"] = "<br/>".join(title)


def _add_edges(graph, inputs, outputs, steps):

    for k, v in steps.as_dict.items():
        _to = k
        for _, prt in ListOrMap(v.get("in", {}), key_field="id", problems=[]).as_dict.items():
            graph["edges"] += [{"from": _f, "to": _to} for _f in _get_source_step(prt, "source")]

    for k, v in outputs.as_dict.items():
        _to = k
        graph["edges"] += [{"from": _f, "to": _to} for _f in _get_source_step(v, "outputSource")]


def _get_source_step(v, key):
    src = v.get(key) if isinstance(v, dict) else v
    if not isinstance(src, list):
        src = [src]
    return [normalize_source(s).split("/")[0] for s in src if isinstance(s, str)]
