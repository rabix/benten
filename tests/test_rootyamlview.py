import pathlib
import shutil
import os
from typing import Union, Dict, Tuple

from benten.editing.rootyamlview import RootYamlView, YamlView, TextView

current_path = pathlib.Path(__file__).parent
test_dir = "yaml-test-temp-dir"


def setup():
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)


def teardown():
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


nested_document = """
steps:
- id: step1
  run:
    steps:
    - id: step11
      run:
        steps:
          step111:
            run:
              steps:
              - id: step1111
              - id: step1112
          step112:
            run:
              steps:
              - id: step1121
    - id: step12
      run:
        steps:
          step121:
            run:
              steps:
              - id: step1211
              - id: step1212
    - id: step13
      run:
        steps:
          step131:
            run:
              steps:
              - id: step1311
              - id: step1312
- id: step2
  run:
    steps:
    - id: step21
      run:
        steps:
          step211:
            run:
              steps:
              - id: step2111
              - id: step2112
          step212:
            run:
              steps:
              - id: step2121
    - id: step22
      run:
        steps:
          step221:
            run:
              steps:
              - id: step2211
              - id: step2212
          step222:
            run:
              steps:
              - id: step2221
              - id: step2222
    - id: step23
      run:
        steps:
          step231:
            run:
              steps:
              - id: step2311
              - id: step2312
"""


class FakeEditor:
    def __init__(self):
        self.text = None
        self.closed = False

    def new_text_available(self, text):
        self.text = text

    def close(self):
        self.closed = True


def test_basic():

    ed1 = FakeEditor()
    view1 = RootYamlView(
        raw_text=nested_document,
        file_path=pathlib.Path("./test.cwl"),
        edit_callback=ed1.new_text_available,
        delete_callback=ed1.close)

    assert view1.raw_text == nested_document
    assert ed1.text == nested_document

    ed2 = FakeEditor()
    view2 = view1.create_child_view(
        child_path=("steps", "step2", "run"),
        can_have_children=True,
        edit_callback=ed2.new_text_available,
        delete_callback=ed2.close)

    expected = """steps:
- id: step21
  run:
    steps:
      step211:
        run:
          steps:
          - id: step2111
          - id: step2112
      step212:
        run:
          steps:
          - id: step2121
- id: step22
  run:
    steps:
      step221:
        run:
          steps:
          - id: step2211
          - id: step2212
      step222:
        run:
          steps:
          - id: step2221
          - id: step2222
- id: step23
  run:
    steps:
      step231:
        run:
          steps:
          - id: step2311
          - id: step2312
"""
    assert view2.raw_text == expected
    assert view2.readable_path() == "step2"
    assert ed2.text == expected


def open_tree() -> Tuple[Dict[str, Union[RootYamlView, YamlView, TextView]], Dict[str, FakeEditor]]:

    def new_child(parent_p, child_p, chc):
        k1 = "{}/{}".format(parent_p, child_p)
        editors[k1] = FakeEditor()
        views[k1] = views[parent_p].create_child_view(
            child_path=("steps", child_p) + (("run",) if chc else ()),
            can_have_children=chc,
            edit_callback=editors[k1].new_text_available,
            delete_callback=editors[k1].close)

    views = dict()
    editors = dict()

    editors["root"] = FakeEditor()
    views["root"] = RootYamlView(
        raw_text=nested_document,
        file_path=pathlib.Path("./test.cwl"),
        edit_callback=editors["root"].new_text_available,
        delete_callback=editors["root"].close)

    new_child("root", "step2", True)
    new_child("root/step2", "step22", True)
    new_child("root/step2/step22", "step221", True)
    new_child("root/step2/step22", "step222", True)
    new_child("root/step2/step22/step222", "step2221", False)

    # editors["root/step2"] = FakeEditor()
    # views["root/step2"] = views["root"].create_child_view(
    #     child_path=("steps", "step2", "run"),
    #     can_have_children=True,
    #     edit_callback=editors["root/step2"].new_text_available,
    #     delete_callback=editors["root/step2"].close)
    #
    # views["root/step2/step22"] = views["root/step2"].create_child_view(
    #     child_path=("steps", "step22", "run"), can_have_children=True, callback=mb.add_tab)
    #
    # views["root/step2/step22/step221"] = views["root/step2/step22"].create_child_view(
    #     child_path=("steps", "step221", "run"), can_have_children=True, callback=mb.add_tab)
    #
    # views["root/step2/step22/step222"] = views["root/step2/step22"].create_child_view(
    #     child_path=("steps", "step222", "run"), can_have_children=True, callback=mb.add_tab)
    #
    # views["root/step2/step22/step222/step2221"] = views["root/step2/step22/step222"].create_child_view(
    #     child_path=("steps", "step2221"), can_have_children=False, callback=mb.add_tab)

    return views, editors


def test_null_synchronization():
    views, editors = open_tree()

    assert views["root/step2/step22/step221"].raw_text == """steps:
- id: step2211
- id: step2212
"""
    assert views["root/step2/step22/step221"].readable_path() == "step2.step22.step221"
    assert editors["root/step2/step22/step221"].text == """steps:
- id: step2211
- id: step2212
"""

    views["root/step2/step22/step221"].set_raw_text("""steps:
- id: step2211
- id: step2212""")
    views["root/step2/step22/step221"].synchronize_text()
    assert views["root"].raw_text == nested_document
    assert editors["root"].text == nested_document

    views["root/step2/step22/step221"].set_raw_text("""steps:
- id: step2211
- id: step2212
""")
    views["root/step2/step22/step221"].synchronize_text()
    assert views["root"].raw_text == nested_document


def test_parse_error_synchronization():
    views, editors = open_tree()

    new_text = """steps:
  step221:
    run
      steps:
      - id: step2211
      - id: step2212
"""
    views["root/step2/step22"].set_raw_text(new_text)
    assert views["root/step2/step22"].yaml is None
    assert views["root/step2/step22"].yaml_error is not None


def test_ancestor_synchronization():
    views, editors = open_tree()

    assert views["root/step2/step22/step221"].raw_text == """steps:
- id: step2211
- id: step2212
"""
    views["root/step2/step22/step221"].set_raw_text("""steps:
- id: step2211""")
    views["root/step2/step22/step221"].synchronize_text()
    expected = """
steps:
- id: step1
  run:
    steps:
    - id: step11
      run:
        steps:
          step111:
            run:
              steps:
              - id: step1111
              - id: step1112
          step112:
            run:
              steps:
              - id: step1121
    - id: step12
      run:
        steps:
          step121:
            run:
              steps:
              - id: step1211
              - id: step1212
    - id: step13
      run:
        steps:
          step131:
            run:
              steps:
              - id: step1311
              - id: step1312
- id: step2
  run:
    steps:
    - id: step21
      run:
        steps:
          step211:
            run:
              steps:
              - id: step2111
              - id: step2112
          step212:
            run:
              steps:
              - id: step2121
    - id: step22
      run:
        steps:
          step221:
            run:
              steps:
              - id: step2211
          step222:
            run:
              steps:
              - id: step2221
              - id: step2222
    - id: step23
      run:
        steps:
          step231:
            run:
              steps:
              - id: step2311
              - id: step2312
"""
    assert views["root"].raw_text == expected


def test_child_synchronization():
    views, editors = open_tree()

    edited_document = """
steps:
- id: step1
  run:
    steps:
    - id: step11
      run:
        steps:
          step111:
            run:
              steps:
              - id: step1111
              - id: step1112
          step112:
            run:
              steps:
              - id: step1121
    - id: step12
      run:
        steps:
          step121:
            run:
              steps:
              - id: step1211
              - id: step1212
    - id: step13
      run:
        steps:
          step131:
            run:
              steps:
              - id: step1311
              - id: step1312
- id: step2
  run:
    steps:
    - id: step21
      run:
        steps:
          step211:
            run:
              steps:
              - id: step2111
              - id: step2112
          step212:
            run:
              steps:
              - id: step2121
    - id: step22
      run:
        steps:
          step221:
            run:
              steps:
              - id: step2212  # <- other sibling deleted
          step222:
            run:
              steps:
              - id: step2221
              - id: step2222
    - id: step23
      run:
        steps:
          step231:
            run:
              steps:
              - id: step2311
              - id: step2312
"""
    views["root"].set_raw_text(edited_document)
    views["root"].synchronize_text()
    expected_gen2 = """steps:
- id: step21
  run:
    steps:
      step211:
        run:
          steps:
          - id: step2111
          - id: step2112
      step212:
        run:
          steps:
          - id: step2121
- id: step22
  run:
    steps:
      step221:
        run:
          steps:
          - id: step2212  # <- other sibling deleted
      step222:
        run:
          steps:
          - id: step2221
          - id: step2222
- id: step23
  run:
    steps:
      step231:
        run:
          steps:
          - id: step2311
          - id: step2312
"""
    assert views["root/step2"].raw_text == expected_gen2

    expected_gen4 = """steps:
- id: step2212  # <- other sibling deleted
"""
    assert views["root/step2/step22/step221"].raw_text == expected_gen4


def test_child_removed():
    views, editors = open_tree()

    assert views["root/step2/step22"].raw_text == """steps:
  step221:
    run:
      steps:
      - id: step2211
      - id: step2212
  step222:
    run:
      steps:
      - id: step2221
      - id: step2222
"""
    assert ("steps", "step2", "run", "steps", "step22", "run", "steps", "step221", "run") in views["root"]

    new_text = """steps:
  step222:
    run:
      steps:
      - id: step2221
"""
    views["root/step2/step22"].set_raw_text(new_text)
    views["root/step2/step22"].synchronize_text()
    assert views["root/step2/step22"].raw_text == new_text

    assert ("steps", "step2", "run", "steps", "step22", "run", "steps", "step221", "run") not in views["root"]
    assert views["root/step2/step22/step221"].marked_for_deletion
    assert editors["root/step2/step22/step221"].closed

    assert not views["root/step2/step22/step222"].marked_for_deletion
    assert not editors["root/step2/step22/step222"].closed


def test_edit_twice():
    views, editors = open_tree()
    views["root/step2/step22/step221"].set_raw_text("""steps:
- id: step2211-new
- id: step2212""")
    views["root/step2/step22/step221"].synchronize_text()

    expected = """steps:
  step221:
    run:
      steps:
      - id: step2211-new
      - id: step2212
  step222:
    run:
      steps:
      - id: step2221
      - id: step2222
"""
    assert views["root/step2/step22"].raw_text == expected

    views["root/step2/step22/step221"].set_raw_text("""steps:
- id: step2211-new
- id: step2212-new""")
    views["root/step2/step22/step221"].synchronize_text()

    assert views["root/step2/step22/step221"].raw_text == """steps:
- id: step2211-new
- id: step2212-new
"""


def test_yaml_errors():
    views, editors = open_tree()

    orig_text = views["root/step2/step22"].raw_text
    views["root/step2/step22/step221"].set_raw_text("""steps
- id: step2211-new
- id: step2212""")
    views["root/step2/step22/step221"].synchronize_text()

    assert views["root/step2/step22/step221"].yaml_error is not None
    assert views["root/step2/step22"].raw_text == orig_text


def test_io():
    views, editors = open_tree()

    assert not views["root/step2/step22/step221"].saved()
    assert views["root/step2/step22/step221"].changed_externally()

    views["root/step2/step22/step221"].save()

    assert views["root/step2/step22/step221"].saved()
    assert not views["root"].changed_externally()

    views["root/step2/step22/step221"].set_raw_text("""steps:
- id: step2211-new
- id: step2212""")
    views["root/step2/step22/step221"].synchronize_text()

    assert not views["root/step2/step22/step221"].saved()
    assert not views["root"].changed_externally()

    views["root"].save()

    views["root"].file_path.open("w").write(nested_document)

    assert views["root/step2/step22/step221"].changed_externally()
