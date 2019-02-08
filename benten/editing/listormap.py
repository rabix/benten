from abc import ABC, abstractmethod

import yaml
try:
    from yaml import CSafeLoader as Loader
except ImportError:
    from yaml import SafeLoader as Loader


# cwl = open("salmon.cwl", "r").read()
#
# %timeit c1 = parse_cwl_to_dict(cwl)
# 28.5 ms ± 676 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)
#
# %timeit c2 = parse_cwl_to_lom(cwl)
# 31.3 ms ± 659 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)


def parse_cwl_to_dict(raw_cwl):
    return yaml.load(raw_cwl, Loader=Loader)


def parse_cwl_to_lom(raw_cwl):
    return recursive_parse(yaml.load(raw_cwl, Loader=CLineLoader))


class ListOrMap(ABC):
    def __init__(self, obj):
        self.obj = obj
        self.start_line = None
        self.end_line = None
        self.flow_style = None

        super().__init__()
        self._sub_init_()

    @abstractmethod
    def _sub_init_(self):
        # Code to fill out line metadata and strip from original object
        pass

    @abstractmethod
    def get(self, key, default):
        pass

    @abstractmethod
    def __getitem__(self, item):
        pass

    @abstractmethod
    def __contains__(self, item):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    def __len__(self):
        return len(self.obj)


class CWLList(ListOrMap):

    def _sub_init_(self):
        _list = self.obj
        if len(_list) > 0:
            _l = _list[-1]
            if isinstance(_l, dict):
                if "__start_line__" in _l:
                    self.start_line = _l["__start_line__"]
                    self.end_line = _l["__end_line__"]
                    self.flow_style = _l["__flow_style__"]
                    self.obj = _list[:-1]

    def get(self, key, default=None):
        for v in self.obj:
            if v["id"] == key:
                return v
        else:
            return default

    def __getitem__(self, key):
        for v in self.obj:
            if v["id"] == key:
                return v
        else:
            raise KeyError

    def __contains__(self, item):
        return any(True for v in self.obj if v["id"] == item)

    def __iter__(self):
        for n, v in enumerate(self.obj):
            # CWL demands that a list of the type we are thinking of has an id field
            yield v["id"], v


class CWLMap(ListOrMap):

    def _sub_init_(self):
        _dict = self.obj
        if "__meta__" in _dict:
            _meta = _dict["__meta__"]
            self.start_line = _meta["__start_line__"]
            self.end_line = _meta["__end_line__"]
            self.flow_style = _meta["__flow_style__"]
            self.obj.pop("__meta__")

    def get(self, key, default=None):
        return self.obj.get(key, default)

    def __getitem__(self, key):
        return self.obj[key]

    def __contains__(self, item):
        return item in self.obj

    def __iter__(self):
        for k, v in self.obj.items():
            yield k, v


def recursive_parse(obj: (dict, list, object)):
    if isinstance(obj, dict):
        c = CWLMap(obj)
        c.obj = {
            k: recursive_parse(v)
            for k, v in c.obj.items()
        }
        return c
    elif isinstance(obj, list):
        c = CWLList(obj)
        c.obj = [
            recursive_parse(v)
            for v in c.obj
        ]
        return c
    else:
        return obj


# In [3]: %timeit cwl = cwldoc.CwlDoc(fname=pathlib.Path("salmon.cwl"))
# 28.8 ms ± 832 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

# From a hint here: https://stackoverflow.com/a/53647080
# This is not suitable for general YAML parsing, but works for our use case
class CLineLoader(Loader):

    def construct_mapping(self, node, deep=False):
        mapping = super().construct_mapping(node, deep=deep)
        mapping["__meta__"] = {
            "__start_line__": node.start_mark.line,
            "__end_line__": node.end_mark.line,
            "__flow_style__": node.flow_style
        }
        return mapping

    def construct_sequence(self, node, deep=False):
        seq = super().construct_sequence(node, deep=deep)
        seq.append({
            "__start_line__": node.start_mark.line,
            "__end_line__": node.end_mark.line,
            "__flow_style__": node.flow_style
        })
        return seq
