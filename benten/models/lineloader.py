"""A little shim on top of PyYaml that retrieves line and column numbers for objects in the YAML.
And we get to subclass int!!!

Some profiling information

For "wgs.cwl"

In [2]: %timeit data = parse_yaml_with_line_info(cwl)
127 ms ± 1.07 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

In [2]: %timeit data = parse_yaml_with_line_info(cwl, convert_to_lam=True)
126 ms ± 1.23 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)

In [3]: %timeit data = yaml.load(cwl, CSafeLoader)
95.5 ms ± 374 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

In [4]: %timeit ruamel.yaml.load(cwl, Loader=ruamel.yaml.RoundTripLoader)
2.43 s ± 165 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)


For "salmon.cwl"

In [7]: %timeit ruamel.yaml.load(cwl, Loader=ruamel.yaml.RoundTripLoader)
695 ms ± 6.26 ms per loop (mean ± std. dev. of 7 runs, 1 loop each)

In [8]: %timeit data = parse_yaml_with_line_info(cwl)
36.8 ms ± 363 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

In [9]: %timeit data = yaml.load(cwl, CSafeLoader)
28.2 ms ± 250 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)


(ruamel.yaml         0.15.88)

**NOTE**
For now, this code only puts in meta information in lists, seq and strings. This is sufficient
for the editing we need to do in CWL docs. We can extend as needed
"""
from typing import Tuple, Union, Any, List

import yaml
from yaml.parser import ParserError, ScannerError
try:
    from yaml import CSafeLoader as Loader
except ImportError:
    import warnings
    warnings.warn("You don't have yaml.CSafeLoader installed, "
                  "falling back to slower yaml.SafeLoader",
                  ImportWarning)
    from yaml import SafeLoader as Loader

from .documentproblem import DocumentProblem


def load_yaml(raw_cwl: str):
    return yaml.load(raw_cwl, Loader)


class YNone:
    def __init__(self, node):
        self.start = node.start_mark
        self.end = node.end_mark

    def __bool__(self):
        return False

    def items(self):  # We often test this against a dict
        for n in []:
            yield

    # Pretend we are an empty iterable
    def __next__(self):
        raise StopIteration()

    def __iter__(self):
        return self


class Yint(int):  # pragma: no cover
    def __new__(cls, value, node):
        x = int.__new__(cls, value)
        x.start = node.start_mark
        x.end = node.end_mark
        x.style = node.style
        return x


class Ystr(str):
    def __new__(cls, value, node):
        x = str.__new__(cls, value)
        x.start = node.start_mark
        x.end = node.end_mark
        x.style = node.style
        return x


class Yfloat(float):  # pragma: no cover
    def __new__(cls, value, node):
        x = float.__new__(cls, value)
        x.start = node.start_mark
        x.end = node.end_mark
        x.style = node.style
        return x


class Ybool(int):  # pragma: no cover
    def __new__(cls, value, node):
        x = int.__new__(cls, bool(value))
        x.start = node.start_mark
        x.end = node.end_mark
        x.style = node.style
        return x


class Ydict(dict):
    def __init__(self, value, node):
        dict.__init__(self, value)
        self.start = node.start_mark
        self.end = node.end_mark
        self.flow_style = node.flow_style

    @classmethod
    def empty(cls):
        """This is to account for empty documents"""
        class DummyNode:
            class DummyMark:
                line = 0
                column = 0

            start_mark = DummyMark()
            end_mark = DummyMark()
            flow_style = False

        return cls({}, DummyNode())


class Ylist(list):
    def __init__(self, value, node):
        list.__init__(self, value)
        self.start = node.start_mark
        self.end = node.end_mark
        self.flow_style = node.flow_style


# We've flattened them all together. The names don't clash (due to inheritance), so we are ok
# if we run into trouble, we'll have to add context information (CWL type, parent type etc.)
allowed_loms = {
    "inputs": "id",
    "outputs": "id",
    "requirements": "class",
    "hints": "class",
    "fields": "name",
    "steps": "id",
    "in": "id"
}


class LAM(dict):
    def __init__(self, value, node, key_field: str="id", errors=[]):
        secret_missing_key = "there is no CWL field that looks like this, and it can safely be used"

        def _get_key(x, _errors):
            if not isinstance(x, dict):
                _errors += [
                    DocumentProblem(line=node.start_mark.line, column=node.start_mark.column,
                                    message="Expecting a dictionary here",
                                    problem_type=DocumentProblem.Type.error,
                                    problem_class=DocumentProblem.Class.cwl)]
                return None
            elif key_field not in x:
                _errors += [
                    DocumentProblem(line=node.start_mark.line, column=node.start_mark.column,
                                    message="Expecting a dictionary here",
                                    problem_type=DocumentProblem.Type.error,
                                    problem_class=DocumentProblem.Class.cwl)]
                return None
            else:
                return x[key_field]

        dict.__init__(self, {
            _k: _v
            for _k, _v in ((_get_key(v, errors), v) for v in value)
            if _k is not None
        })

        if secret_missing_key in self:
            self.pop(secret_missing_key)

        self.start = node.start_mark
        self.end = node.end_mark
        self.flow_style = node.flow_style


def y_construct(v, node):  # pragma: no cover
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


class YSafeLineLoader(Loader):

    # The SafeLoader always passes str to this
    def construct_scalar(self, node):
        return Ystr(super(YSafeLineLoader, self).construct_scalar(node), node)

    def construct_yaml_null(self, node):
        self.construct_scalar(node)
        return YNone(node)

    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        mapping[meta_node_key] = node
        return mapping

    def construct_sequence(self, node, deep=False):
        seq = super().construct_sequence(node, deep=deep)
        seq.append(node)
        return seq


YSafeLineLoader.add_constructor(
    'tag:yaml.org,2002:null',
    YSafeLineLoader.construct_yaml_null)


def _recurse_extract_meta(x, key=None, convert_to_lam=False, errors=[]):
    if isinstance(x, dict):
        node = x.pop(meta_node_key)
        return Ydict({k: _recurse_extract_meta(v, k, convert_to_lam, errors) for k, v in x.items()}, node)
    elif isinstance(x, list):
        node = x.pop(-1)
        _data = [_recurse_extract_meta(v, None, convert_to_lam, errors) for v in x]
        if convert_to_lam and key in allowed_loms:
            return LAM(_data, node, key_field=allowed_loms[key], errors=errors)
        return Ylist(_data, node)
    else:
        return x


class DocumentError(Exception):
    def __init__(self, line, col, msg):
        self.line = line
        self.column = col
        self.message = msg


def parse_yaml_with_line_info(raw_cwl: str, convert_to_lam=False, errors=[]):
    try:
        return _recurse_extract_meta(yaml.load(raw_cwl, YSafeLineLoader),
                                     convert_to_lam=convert_to_lam, errors=errors)
    except (ParserError, ScannerError) as e:
        raise DocumentError(e.problem_mark.line, e.problem_mark.column, str(e))


# todo: This algorithm can be cleaned up
# todo: consider column for the indent level - this will solve issues with appending sections
def compute_path(
        doc: Union[Ydict, Ylist], line, column,
        path: Tuple[Union[str, int], ...]=()) -> Tuple[Union[str, int], ...]:

    if not isinstance(doc, (Ydict, Ylist)):
        return path

    if doc.start.line != doc.end.line:
        indent = doc.start.column
    else:
        indent = None

    if column == indent:
        return path

    values = doc.items() if isinstance(doc, dict) else enumerate(doc)
    for k, v in values:

        if v.start.line == v.end.line == line:
            return path + (k,)

        if v.start.line <= line <= v.end.line:
            return compute_path(v, line, column, path + (k,))

    else:
        return path


def lookup(doc: Union[Ydict, Ylist], path: Tuple[Union[str, int]]):
    sub_doc = doc
    for p in path or []:
        sub_doc = sub_doc[p]
    return sub_doc


def reverse_lookup(line, col, doc: Union[Ydict, Ylist], path: Tuple[Union[str, int]]=()):
    """Not as expensive as you'd think ... """
    values = doc.items() if isinstance(doc, dict) else enumerate(doc)
    k, v = None, None
    for k, v in values:
        if v.start.line <= line <= v.end.line:
            if v.start.line != v.end.line or v.start.column <= col <= v.end.column:
                if not isinstance(v, Ydict) and not isinstance(v, Ylist):
                    return path + (k,), v
                else:
                    return reverse_lookup(line, col, v, path + (k,))
    else:
        return k, v


def coordinates(v):
    return (v.start.line, v.start.column), (v.end.line, v.end.column)
