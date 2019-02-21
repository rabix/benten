"""A little shim on top of PyYaml that retrieves line and column numbers for objects in the YAML.
And we get to subclass int!!!

Some profiling information

For "wgs.cwl"

In [2]: %timeit data = parse_cwl_with_line_info(cwl)
132 ms ± 1.51 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

In [3]: %timeit data = yaml.load(cwl, CSafeLoader)
99.5 ms ± 2.4 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

In [4]: %timeit ruamel.yaml.load(cwl, Loader=ruamel.yaml.RoundTripLoader)
2.34 s ± 31.5 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)


For "salmon.cwl"

In [6]: %timeit ruamel.yaml.load(cwl, Loader=ruamel.yaml.RoundTripLoader)
715 ms ± 6.83 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

In [7]: %timeit data = parse_cwl_with_line_info(cwl)
40.1 ms ± 2.56 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

In [8]: %timeit data = yaml.load(cwl, CSafeLoader)
31.6 ms ± 2.46 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)


(ruamel.yaml         0.15.88)

"""
import yaml
try:
    from yaml import CSafeLoader as Loader
except ImportError:
    import warnings
    warnings.warn("You don't have yaml.CSafeLoader installed, "
                  "falling back to slower yaml.SafeLoader",
                  ImportWarning)
    from yaml import SafeLoader as Loader


class Yint(int):
    def __new__(cls, value, node):
        x = int.__new__(cls, value)
        x.start_mark = node.start_mark
        x.end_mark = node.end_mark
        x.style = node.style
        return x


class Ystr(str):
    def __new__(cls, value, node):
        x = str.__new__(cls, value)
        x.start_mark = node.start_mark
        x.end_mark = node.end_mark
        x.style = node.style
        return x


class Yfloat(float):
    def __new__(cls, value, node):
        x = float.__new__(cls, value)
        x.start_mark = node.start_mark
        x.end_mark = node.end_mark
        x.style = node.style
        return x


class Ybool(int):
    def __new__(cls, value, node):
        x = int.__new__(cls, bool(value))
        x.start_mark = node.start_mark
        x.end_mark = node.end_mark
        x.style = node.style
        return x


class Ydict(dict):
    def __init__(self, value, node):
        dict.__init__(self, value)
        self.start_mark = node.start_mark
        self.end_mark = node.end_mark
        self.flow_style = node.flow_style


class Ylist(list):
    def __init__(self, value, node):
        list.__init__(self, value)
        self.start_mark = node.start_mark
        self.end_mark = node.end_mark
        self.flow_style = node.flow_style


def y_construct(v, node):
    if isinstance(v, str):
        return Ystr(v, node)
    elif isinstance(v, int):
        return Yint(v, node)
    elif isinstance(v, float):
        return Yfloat(v, node)
    elif isinstance(v, bool):
        return Ybool(v, node)
    elif isinstance(v, dict):
        return Ydict(v, node)
    elif isinstance(v, list):
        return Ylist(v, node)
    else:
        return v


meta_node_key = "_lineloader_secret_key_"


def _recurse_extract_meta(x):
    if isinstance(x, dict):
        node = x.pop(meta_node_key)
        return Ydict({k: _recurse_extract_meta(v) for k, v in x.items()}, node)
    elif isinstance(x, list):
        node = x.pop(-1)
        return Ylist([_recurse_extract_meta(v) for v in x], node)
    else:
        return x


class YSafeLineLoader(Loader):

    def construct_scalar(self, node):
        return y_construct(super(YSafeLineLoader, self).construct_scalar(node), node)

    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        mapping[meta_node_key] = node
        return mapping

    def construct_sequence(self, node, deep=False):
        seq = super().construct_sequence(node, deep=deep)
        seq.append(node)
        return seq


def parse_cwl_with_line_info(raw_cwl: str):
    return _recurse_extract_meta(yaml.load(raw_cwl, YSafeLineLoader))
