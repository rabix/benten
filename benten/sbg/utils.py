def _strip_sbg_tags(node):
    if isinstance(node, dict):
        return {
            k: _strip_sbg_tags(v)
            for k, v in node.items()
            if k[:4] != "sbg:" and k != "sbg:hints"
        }
    elif isinstance(node, list):
        return [
            _strip_sbg_tags(n)
            for n in node
        ]
    else:
        return node
