"""Parse CWL and create a JSON file describing the workflow. This dictionary
is directly suitable for display by vis.js, but can be parsed for any other
purpose."""

#  Copyright (c) 2019 Seven Bridges. See LICENSE

from ..cwl.lib import ListOrMap


def cwl_graph(cwl: dict):

    graph = {
        "nodes": [],
        "edges": []
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
            "title": v.get("label", k) if isinstance(v, dict) else k,
            "group": grp_id}]


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
    return [s.split("/")[0] for s in src if isinstance(s, str)]
