import pytest

import pathlib

from benten.editing.lineloader import \
    parse_yaml_with_line_info, coordinates, lookup, reverse_lookup, \
    LAM, Ylist, Ydict, \
    _recurse_extract_meta, y_construct, meta_node_key, DocumentError, \
    compute_path


current_path = pathlib.Path(__file__).parent


def test_load_malformed_parse():
    with pytest.raises(DocumentError) as e:
        _ = parse_yaml_with_line_info(raw_cwl="id: [")

    assert e.value.line == 1    # Gotta figure out why PyYaml thinks this is line 2
    assert e.value.column == 0


def test_load_malformed_scan():
    with pytest.raises(DocumentError) as e:
        _ = parse_yaml_with_line_info(raw_cwl=\
"""
key:
    missing colon
    another key:""")

    assert e.value.line == 3
    assert e.value.column == 15


def test_basic_load():
    path = pathlib.Path(current_path, "cwl/sample.yaml")
    doc = parse_yaml_with_line_info(raw_cwl=path.open("r").read())

    assert doc["flowstyle dict"].start.line == 2
    assert doc["flowstyle dict"].end.line == 4

    assert coordinates(doc["flowstyle dict"]) == ((2, 16), (4, 41))

    assert coordinates(doc["flowstyle dict"]["ln1"]) == ((2, 22), (2, 47))

    assert coordinates(doc["flowstyle dict"]["ln2"]) == ((2, 57), (2, 70))

    assert coordinates(doc["list"][0]) == ((18, 18), (18, 41))

    assert coordinates(
        doc["level1"]["level2"]["multiline doc preserve newlines"]) == ((24, 37), (30, 0))

    # assert coordinates(doc["just to cover all types"][1]) == ((48, 29), (48, 35))


def test_parse_to_lom():
    text = """class: Workflow
cwlVersion: v1.0
doc: ''
id: 
label: 
inputs: [in1]
outputs: [out1]
steps:
  step1:
    run:
      class: CommandLineTool
      cwlVersion: v1.0
      doc: ''
      id: 
      label: 
      inputs:
        in1: in1
      outputs: []
      baseCommand: ''
      hints: []
      requirements: []
requirements: []
hints: []
"""
    doc = parse_yaml_with_line_info(raw_cwl=text, convert_to_lam=True)


def test_lookup():
    path = pathlib.Path(current_path, "cwl/sample.yaml")
    doc = parse_yaml_with_line_info(raw_cwl=path.open("r").read())

    assert lookup(doc, ["list", 1]) == "When you fall"
    assert coordinates(lookup(doc, ["list", 1])) == ((19, 18), (19, 31))

    assert lookup(doc, ["level1", "level2", "list", 3, "list2", 1]) == "When you break"


def test_reverse_lookup():
    path = pathlib.Path(current_path, "cwl/sample.yaml")
    doc = parse_yaml_with_line_info(raw_cwl=path.open("r").read())

    assert reverse_lookup(19, 22, doc) == (("list", 1), "When you fall")

    assert reverse_lookup(26, 22, doc) == \
           (("level1", "level2", "multiline doc preserve newlines"),
            "When you call\n"
            "Who's gonna pay attention\n"
            "To your dreams\n"
            "Who's gonna plug their ears\n"
            "When you scream")

    assert reverse_lookup(2, 64, doc) == (("flowstyle dict", "ln2"), "It's too late")


def test_line_number_dict():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl")
    c = parse_yaml_with_line_info(raw_cwl=wf_path.open("r").read())

    assert c["cwlVersion"] == "v1.0"
    assert c.start.line == 0
    assert c.end.line == 24

    assert c["inputs"].start.line == 3
    assert c["inputs"].start.column == 2

    assert c["inputs"]["inp"].start.line == 3
    assert c["inputs"]["inp"].start.column == 7

    assert c["outputs"].start.line == 7

    assert len(c["steps"]) == 2

    assert c["steps"]["untar"].start.line == 13
    assert c["steps"]["untar"].end.line == 19

    assert c["steps"]["untar"]["out"].flow_style
    assert c["steps"]["untar"]["out"][0].start.line == 17
    assert c["steps"]["untar"]["out"][0].start.column == 10

    assert c["steps"]["compile"].start.line == 20
    assert c["steps"]["compile"].end.line == 24


def test_line_number2():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-list.cwl")
    c = parse_yaml_with_line_info(raw_cwl=wf_path.open("r").read())

    assert c["cwlVersion"] == "v1.0"

    assert len(c["steps"]) == 2

    assert c["steps"].start.line == 12
    assert c["steps"].end.line == 24

    assert c["steps"][0].start.line == 12
    assert c["steps"][0].start.column == 4


def test_line_number_salmon():

    wf_path = pathlib.Path(current_path, "cwl/sbg/salmon.cwl")
    c = parse_yaml_with_line_info(raw_cwl=wf_path.open("r").read())

    assert c["steps"][0]["run"]["outputs"][0]["doc"].style == ">"
    assert c["steps"][0]["run"]["outputs"][0]["outputBinding"]["glob"].style == "|"
    assert c["steps"][0]["run"]["outputs"][0]["outputBinding"]["glob"].start.line == 672
    assert c["steps"][0]["run"]["outputs"][0]["outputBinding"]["glob"].end.line == 693


class Mark:
    def __init__(self):
        self.line = 22
        self.column = 19


class FakeNode:
    def __init__(self):
        self.start_mark = Mark()
        self.end_mark = Mark()
        self.flow_style = False
        self.style = True


def test_lam_basic():
    a_list = Ylist([
        {"id": "ln1", "line": "Billy left his home with a dollar in his pocket and a head full of dreams."},
        {"id": "ln2", "line": "He said somehow, some way, it's gotta get better than this."},
        {"id": "ln3", "line": "Patti packed her bags, left a note for her momma, she was just seventeen,"},
        {"id": "ln4", "line": "There were tears in her eyes when she kissed her little sister goodbye."},
        {             "line": "They held each other tight as they drove on through the night they were so excited."},
        {             "line": "We got just one shot of life, let's take it while we're still not afraid."}
    ], FakeNode())

    errors = []
    a_map = LAM(a_list, FakeNode(), key_field="id", errors=errors)

    assert len(a_map) == 4
    assert a_map.start.line == 22
    assert a_map.end.column == 19
    assert not a_map.flow_style

    assert "ln2" in a_map
    assert a_map["ln4"]["line"] == "There were tears in her eyes when she kissed her little sister goodbye."

    assert len(errors) == 2

    another_list = Ylist([
        {
            ("class" if k == "id" else k): _v
            for k, _v in v.items()
        }
        for v in a_list
    ], FakeNode())

    errors = []
    b_map = LAM(another_list, FakeNode(), key_field="class", errors=errors)

    assert len(b_map) == 4

    assert "ln2" in b_map
    assert b_map["ln4"]["line"] == "There were tears in her eyes when she kissed her little sister goodbye."

    assert len(errors) == 2


def Y(obj):
    if isinstance(obj, list):
        return obj + [FakeNode()]
    elif isinstance(obj, dict):
        obj[meta_node_key] = FakeNode()
        return obj
    else:
        v = y_construct(obj, FakeNode())
        return y_construct(obj, FakeNode())


def test_auto_switcher():
    a_list = [
        Y({"id": Y("ln1"), "line": Y("I don't know why I love her like I do")}),
        Y({"id": Y("ln2"), "line": Y("All the changes you put me through")}),
        Y({"id": Y("ln3"), "line": Y("Take my money, my cigarettes")}),
        Y({"id": Y("ln4"), "line": Y("I haven't seen the worst of it yet")}),
        FakeNode()
    ]
    res = _recurse_extract_meta(a_list, key="inputs", convert_to_lam=False)
    assert isinstance(res, Ylist)

    # _recurse_extract_meta mutates the original, so we have to create the lists afresh
    a_list = [
        Y({"id": Y("ln1"), "line": Y("I want to know that you'll tell me")}),
        Y({"id": Y("ln2"), "line": Y("I love to stay")}),
        Y({"id": Y("ln3"), "line": Y("Take me to the river, drop me in the water")}),
        Y({"id": Y("ln4"), "line": Y("Take me to the river, dip me in the water")}),
        Y({"id": Y("ln5"), "line": Y("Washing me down, washing me down")}),
        FakeNode()
    ]
    errors = []
    res = _recurse_extract_meta(a_list, key="inputs", convert_to_lam=True, errors=errors)
    assert isinstance(res, LAM)
    assert len(errors) == 0

    a_list = [
        Y({"id": Y("ln1"), "line": Y("I don't know why you treat me so bad")}),
        Y({"id": Y("ln2"), "line": Y("Think of all the things we could have had")}),
        Y({"id": Y("ln3"), "line": Y("Love is an ocean that I can't forget")}),
        Y({"id": Y("ln4"), "line": Y("My sweet sixteen I would never regret")}),
        FakeNode()
    ]
    errors = []
    res = _recurse_extract_meta(a_list, key="outputs", convert_to_lam=True, errors=errors)
    assert isinstance(res, LAM)
    assert len(errors) == 0

    a_map = {
        "ln5": Y("I want to know that you'll tell me"),
        "ln6": Y("I love to stay"),
        "ln7": Y("Take me to the river, drop me in the water"),
        "ln8": Y("Push me in the river, dip me in the water"),
        "ln9": Y("Washing me down, washing me"),
        meta_node_key: FakeNode()
    }
    res = _recurse_extract_meta(a_map, key="inputs", convert_to_lam=False)
    assert isinstance(res, Ydict)

    a_map = {
        "ln5": Y("Hug me, squeeze me, love me, tease me"),
        "ln6": Y("Till I can't, till I can't, till I can't take no more of it"),
        "ln7": Y("Take me to the water, drop me in the river"),
        "ln8": Y("Push me in the water, drop me in the river"),
        "ln9": Y("Washing me down, washing me down"),
        meta_node_key: FakeNode()
    }
    res = _recurse_extract_meta(a_map, key="inputs", convert_to_lam=True)
    assert isinstance(res, Ydict)

    list_with_missing_id = [
        Y({"id": Y("ln1"), "line": Y("I don't know why I love you like I do")}),
        Y({"id": Y("ln2"), "line": Y("All the troubles you put me through")}),
        Y({"id": Y("ln3"), "line": Y("Sixteen candles there on my wall")}),
        Y({                "line": Y("And here am I the biggest fool of them all")}),
        FakeNode()
    ]
    errors = []
    res = _recurse_extract_meta(list_with_missing_id, key="outputs", convert_to_lam=True, errors=errors)
    assert isinstance(res, LAM)
    assert len(errors) == 1
    # assert isinstance(res.errors[0], Ydict)
    # assert res.errors[0].start.line == Mark().line

    list_with_different_key = [
        Y({"class": "ln1", "line": Y("I want to know that you'll tell me")}),
        Y({"class": "ln2", "line": Y("I love to stay")}),
        Y({"class": "ln3", "line": Y("Take me to the river and drop me in the water")}),
        Y({"class": "ln4", "line": Y("Dip me in the river, drop me in the water")}),
        Y({"class": "ln5", "line": Y("Washing me down, washing me down")}),
        FakeNode()
    ]
    errors = []
    res = _recurse_extract_meta(list_with_different_key, key="requirements", convert_to_lam=True, errors=errors)
    assert isinstance(res, LAM)
    assert len(errors) == 0


def test_compute_path():

    wf_path = pathlib.Path(current_path, "cwl/001.basic/wf-steps-as-dict.cwl")
    c = parse_yaml_with_line_info(raw_cwl=wf_path.open("r").read())

    pass


def trace_path(doc, path=(), off=0):

    if not isinstance(doc, (dict, list)):
        # print("{}: ({}, {})".format(path, doc.start.line, doc.end.line))
        return

    values = doc.items() if isinstance(doc, dict) else enumerate(doc)
    for k, v in values:
        print("{}: ({}, {}) - ({}, {})".format(path + (k,),
                                               v.start.line + off, v.start.column,
                                               v.end.line + off, v.end.column))
        trace_path(v, path + (k,), off)


cwl = """cwlVersion: v1.0
class: Workflow
inputs:
  inp: File
  ex: string

outputs:
  classout:
    type: File
    outputSource: compile/classfile

steps:
  untar:
    run: tar-param.cwl
    in:
      tarfile: inp
      extractfile: ex
    out: [example_out]

  

  compile:
    run: arguments.cwl
    in:
      src: untar/example_out
    out: [classfile]

  
"""

c = parse_yaml_with_line_info(raw_cwl=cwl)
trace_path(c, off=344)
