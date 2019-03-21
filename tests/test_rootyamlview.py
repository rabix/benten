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
        self.attached_child = None

    def attach_child(self, child):
        self.attached_child = child


def test_basic():
    yaml_view = RootYamlView(
        raw_text=nested_document, file_path=pathlib.Path("./test.cwl"))

    assert yaml_view.raw_text == nested_document

    ed = FakeEditor()

    ch1 = yaml_view.create_child_view(
        child_path=("steps", "step2", "run"), can_have_children=True,
        callback=ed.attach_child)

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
    assert ch1.raw_text == expected
    assert ch1.readable_path() == "step2"


class MockBenten:
    def __init__(self):
        self.editor_tabs = {}

    def add_tab(self, child: TextView):
        self.editor_tabs[child.inline_path] = child

    def prune_tabs(self):
        self.editor_tabs = {
            k: v for k, v in self.editor_tabs.items()
            if not v.marked_for_deletion
        }


def open_tree() -> Tuple[Dict[str, Union[RootYamlView, YamlView, TextView]], MockBenten]:
    mb = MockBenten()
    views = dict()

    views["root"] = RootYamlView(raw_text=nested_document, file_path=pathlib.Path("./test.cwl"))

    views["root/step2"] = views["root"].create_child_view(
        child_path=("steps", "step2", "run"), can_have_children=True, callback=mb.add_tab)

    views["root/step2/step22"] = views["root/step2"].create_child_view(
        child_path=("steps", "step22", "run"), can_have_children=True, callback=mb.add_tab)

    views["root/step2/step22/step221"] = views["root/step2/step22"].create_child_view(
        child_path=("steps", "step221", "run"), can_have_children=True, callback=mb.add_tab)

    views["root/step2/step22/step222"] = views["root/step2/step22"].create_child_view(
        child_path=("steps", "step222", "run"), can_have_children=True, callback=mb.add_tab)

    views["root/step2/step22/step222/step2221"] = views["root/step2/step22/step222"].create_child_view(
        child_path=("steps", "step2221"), can_have_children=False, callback=mb.add_tab)

    return views, mb


def test_null_synchronization():
    views, mb = open_tree()

    assert views["root/step2/step22/step221"].raw_text == """steps:
- id: step2211
- id: step2212
"""
    assert views["root/step2/step22/step221"].readable_path() == "step2.step22.step221"

    views["root/step2/step22/step221"].set_raw_text("""steps:
- id: step2211
- id: step2212""")
    views["root/step2/step22/step221"].synchronize_text()
    assert views["root"].raw_text == nested_document

    views["root/step2/step22/step221"].set_raw_text("""steps:
- id: step2211
- id: step2212
""")
    views["root/step2/step22/step221"].synchronize_text()
    assert views["root"].raw_text == nested_document


def test_parse_error_synchronization():
    views, mb = open_tree()

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
    views, mb = open_tree()

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
    views, mb = open_tree()

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
    views, mb = open_tree()

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
    # assert ("steps", "step221", "run") in views["root/step2/step22"].children
    # step221_editor = gen3.children[("steps", "step221", "run")].attached_editor

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

    assert not views["root/step2/step22/step222"].marked_for_deletion


def test_edit_twice():
    views, mb = open_tree()
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


def test_io():
    views, mb = open_tree()

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
