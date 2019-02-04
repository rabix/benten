from abc import ABC, abstractmethod
import pathlib
from urllib.parse import urlparse, urldefrag
from io import StringIO
from typing import Generator, Tuple

from ruamel.yaml import YAML  # For round trip
from ruamel.yaml.comments import CommentedMap, CommentedSeq


import yaml


# In [3]: %timeit cwl = blib.CwlDoc(fname=pathlib.Path("salmon.cwl"))
# 28.8 ms ± 832 µs per loop (mean ± std. dev. of 7 runs, 10 loops each)

# From a hint here: https://stackoverflow.com/a/53647080
class CLineLoader(yaml.CSafeLoader):
    def construct_mapping(self, node, deep=False):
        mapping = super(CLineLoader, self).construct_mapping(node, deep=deep)
        mapping['__start_line__'] = node.start_mark.line
        mapping['__end_line__'] = node.end_mark.line
        return mapping


class CwlDoc:
    def __init__(self, fname: pathlib.Path=None, raw_cwl: str=None):
        if fname is not None:
            self.raw_cwl = fname.open("r").read()
        elif raw_cwl is not None:
            self.raw_cwl = raw_cwl
        else:
            raise ValueError("Need to pass path to CWL or raw CWL string")

        self.cwl_dict = yaml.load(self.raw_cwl, Loader=CLineLoader)


def listify(x: (str, [str])):
    if isinstance(x, list):
        return x
    else:
        return [x]


def is_cwl_document(fname: pathlib.Path):
    if fname.exists():
        # For now, a simple extension check. Later we might load the contents and check for cwlVersion
        return fname.suffix == ".cwl"
    else:
        return False


def is_recursible(doc: dict):
    """Does this document have children?"""
    return doc["class"] == "Workflow"


def load_cwl(url: str, round_trip: bool = True):
    """Load the immediate CWL as a dictionary.
    Best to pass as an absolute url"""
    uri = urlparse(url)

    if round_trip:
        # Slowly and carefully load the round-trippable YAML
        raw_doc = YAML(typ="rt").load(open(uri.path, "r").read())
    else:
        # Load it fast via C but not round-trippable
        # We use this to parse the interface. If we used ruamel or the pure
        # Python loader subworkflows with lot of text (large docs, lots of I/O)
        # slows down parsing annoyingly
        raw_doc = YAML(typ="safe", pure=False).load(open(uri.path, "r").read())

    if uri.fragment is not "":
        # This means that we are loading a relative part of another doc
        # We are expecting a $graph, which has this thing in it
        doc = next((part for part in raw_doc["$graph"] if part["id"] == uri.fragment), None)
        if doc is None:
            raise RuntimeError("{} not found in {}".format(uri.fragment, uri.path))
        doc["cwlVersion"] = raw_doc["cwlVersion"]
    else:
        if "$graph" in raw_doc:
            raise RuntimeError("CWL has $graph section. Needs URI entry fragment")

        doc = raw_doc

    return doc


def save_cwl(path: str, cwl_doc: dict):
    """Thin wrapper around ruamel.yaml.dump"""
    with open(path, "w") as fp:
        YAML(typ="rt").dump(cwl_doc, fp)


def cwl_raw_text(cwl_doc: dict):
    out = StringIO()
    YAML(typ="rt").dump(cwl_doc, out)
    return out.getvalue()


def to_text(yml):
    stream = StringIO()
    YAML(typ="rt").dump(yml, stream)
    return stream.getvalue()


def yamlify(text: str):
    return YAML(typ="rt").load(text)


def fast_parse(text: str):
    return YAML(typ="safe", pure=False).load(text)


def reyamlify(yml: CommentedMap):
    """Turn yml into string and reload as YAML. This gets us line numbers after we've messed with
    the original (loaded) YAML"""
    stream = StringIO()
    YAML(typ="rt").dump(yml, stream)
    return YAML(typ="rt").load(stream.getvalue())


# lom = List or Map

def iter_over_plain_lom(obj: (list, dict)) -> Generator[Tuple[str, object], None, None]:
    """For the sub-workflows we load the plain YAML without line numbers and such"""
    if isinstance(obj, list):
        for n, v in enumerate(obj):
            # CWL demands that a list of the type we are thinking of has an id field
            yield v["id"], v
    else:
        for k, v in obj.items():
            yield k, v


# How to get line numbers
# https://bitbucket.org/ruamel/yaml/issues/9/line-number-information-for-mapping-keys

def iter_over_lom(obj: (CommentedSeq, CommentedMap)) -> Generator[Tuple[str, object, int], None, None]:
    if isinstance(obj, CommentedSeq):
        for n, v in enumerate(obj):
            # CWL demands that a list of the type we are thinking of has an id field
            yield v["id"], v, obj.lc.item(n)[0]
    else:
        for k, v in obj.items():
            yield k, v, obj.lc.value(k)[0]


def smart_append(obj: (object, list), x: object):
    if isinstance(obj, list):
        obj.append(x)
    else:
        obj = [obj, x]
    return obj


class ListOrMap(ABC):
    def __init__(self, obj):
        self.obj = obj
        super().__init__()

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

    @abstractmethod
    def append(self, thing_id: str, thing: dict):
        # YAML forces us to write empty lists in flow style, but block style is nicer as a default
        # We only do this for empty lists because for filled lists the author has already
        # expressed a preference
        if len(self.obj) == 0:
            self.obj._yaml_format.set_block_style()


class YList(ListOrMap):

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
            yield v["id"], v, self.obj.lc.item(n)[0]

    def append(self, thing_id: str, thing: CommentedMap):
        if "id" not in thing:
            thing.insert(0, "id", thing_id)  # CWL requires us to have this id here
        self.obj.append(thing)


class YMap(ListOrMap):

    def get(self, key, default=None):
        return self.obj.get(key, default)

    def __getitem__(self, key):
        return self.obj[key]

    def __contains__(self, item):
        return item in self.obj

    def __iter__(self):
        for k, v in self.obj.items():
            yield k, v, self.obj.lc.value(k)[0]

    def append(self, thing_id: str, thing: dict):
        self.obj.insert(len(self.obj), thing_id, thing)


def lom(obj):
    if isinstance(obj, CommentedSeq):
        return YList(obj)
    else:
        return YMap(obj)
