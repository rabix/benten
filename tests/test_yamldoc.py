from benten.editing.yamldoc import PlainText, YamlDoc, Contents
from benten.editing.lineloader import YNone


def test_plain_text():
    original_text = """
Got out of town on a boat goin' to Southern Islands
Sailing a reach before a followin' sea"""
    yaml_doc = PlainText(raw_text=original_text)

    result = yaml_doc.set_raw_text_and_reparse(original_text)
    assert result & Contents.Unchanged
    assert result & Contents.ParseSkipped
    assert not result & Contents.ParseSuccess

    altered_text = """
She was makin' for the trades on the outside
And the downhill run to Papeete"""
    result = yaml_doc.set_raw_text_and_reparse(altered_text)
    assert result & Contents.Changed
    assert result & Contents.ParseSkipped


no_steps = """steps:
"""

assorted_steps = """steps:
- id: step1
  run:
- id: step2
  run: {}
- id: step3
  run:
    ln1: Thinkin' of you's workin' up my appetite 
    ln2: Looking forward to a little afternoon delight
- id: step4
  run: {}
"""


def test_yaml_doc_basic():
    yaml_doc = YamlDoc(raw_text=no_steps)
    assert yaml_doc.parse_yaml() & Contents.ParseSuccess
    assert ("steps",) in yaml_doc
    assert ("steps", "step1") not in yaml_doc

    yaml_doc = YamlDoc(raw_text="Red balloon")
    yaml_doc.set_raw_text_and_reparse(assorted_steps)
    assert ("steps", "step1", "run") in yaml_doc


def test_yaml_doc_delete_lines():
    original_text = """
verse1:
  ln1: Bus stop, wet day
  ln2: She's there, I say
  ln3: Please share my umbrella"""

    yaml_doc = YamlDoc(raw_text=original_text)
    yaml_doc.parse_yaml()
    raw_text = yaml_doc.get_raw_text_for_section(("verse1",))
    assert raw_text == """ln1: Bus stop, wet day
ln2: She's there, I say
ln3: Please share my umbrella"""

    new_text = "ln4: Bus stops, bus goes"
    yaml_doc.set_section_from_raw_text(raw_text=new_text, path=("verse1",))
    yaml_doc.parse_yaml()
    raw_text = yaml_doc.get_raw_text_for_section(("verse1",))
    assert raw_text == new_text + "\n"


def test_yaml_doc_delete_all():
    original_text = """
verse1:
  ln1: Bus stop, wet day
  ln2: She's there, I say
  ln3: Please share my umbrella"""

    yaml_doc = YamlDoc(raw_text=original_text)
    yaml_doc.parse_yaml()
    raw_text = yaml_doc.get_raw_text_for_section(("verse1",))
    assert raw_text == """ln1: Bus stop, wet day
ln2: She's there, I say
ln3: Please share my umbrella"""

    new_text = ""
    yaml_doc.set_section_from_raw_text(raw_text=new_text, path=("verse1",))
    yaml_doc.parse_yaml()
    raw_text = yaml_doc.get_raw_text_for_section(("verse1",))
    assert raw_text == new_text


def test_fast_differ():
    original_lines = """Bus stops, bus goes
She stays, love grows
Under my umbrella""".splitlines(keepends=True)
    new_lines = "".splitlines(keepends=True)
    edit = YamlDoc.edit_from_quick_diff(original_lines, new_lines)
    assert edit.start.line == 0
    assert edit.start.column == 0
    assert edit.end.line == 3
    assert edit.end.column == 0
    assert edit.text == ""


def test_yaml_doc_replace_null():
    yaml_doc = YamlDoc(raw_text=assorted_steps)
    assert yaml_doc.parse_yaml() & Contents.ParseSuccess
    assert ("steps",) in yaml_doc
    assert ("steps", "step1") in yaml_doc

    assert isinstance(yaml_doc[("steps", "step1", "run")], YNone)

    raw_text = yaml_doc.get_raw_text_for_section(("steps", "step1", "run"))
    assert raw_text == ""

    new_text = """Started out this morning feeling so polite
I always though a fish could not be caught who wouldn't bite"""
    yaml_doc.set_section_from_raw_text(new_text, ("steps", "step1", "run"))

    assert yaml_doc.raw_text == """steps:
- id: step1
  run: |-
    Started out this morning feeling so polite
    I always though a fish could not be caught who wouldn't bite
- id: step2
  run: {}
- id: step3
  run:
    ln1: Thinkin' of you's workin' up my appetite 
    ln2: Looking forward to a little afternoon delight
- id: step4
  run: {}
"""


def test_yaml_doc_replace_empty_dict():
    yaml_doc = YamlDoc(raw_text=assorted_steps)
    yaml_doc.parse_yaml()

    new_text = """But you've got some bait a waitin' and I think I might try nibbling"""
    yaml_doc.set_section_from_raw_text(new_text, ("steps", "step2", "run"))

    assert yaml_doc.raw_text == """steps:
- id: step1
  run:
- id: step2
  run: 
    But you've got some bait a waitin' and I think I might try nibbling
- id: step3
  run:
    ln1: Thinkin' of you's workin' up my appetite 
    ln2: Looking forward to a little afternoon delight
- id: step4
  run: {}
"""


def test_yaml_doc_missing_new_line():
    yaml_doc = YamlDoc(raw_text=assorted_steps)
    yaml_doc.parse_yaml()

    new_text = "ln1: Thinkin' of you's workin' up my appetite"
    yaml_doc.set_section_from_raw_text(new_text, ("steps", "step3", "run"))

    expected = """steps:
- id: step1
  run:
- id: step2
  run: {}
- id: step3
  run:
    ln1: Thinkin' of you's workin' up my appetite
- id: step4
  run: {}
"""
    assert yaml_doc.raw_text == expected


def test_yaml_doc_insert_empty_dict():
    yaml_doc = YamlDoc(raw_text=assorted_steps)
    yaml_doc.parse_yaml()

    new_text = ""
    yaml_doc.set_section_from_raw_text(new_text, ("steps", "step3", "run"))

    expected = """steps:
- id: step1
  run:
- id: step2
  run: {}
- id: step3
  run:
- id: step4
  run: {}
"""
    assert yaml_doc.raw_text == expected
