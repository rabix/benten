from benten.editing.yamlview import YamlView, TextType, EditorInterface, Edit, Contents


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


class FakeEditor(EditorInterface):

    def __init__(self):
        super().__init__()
        self.text = ""

    def set_text(self, raw_text: str):
        self.text = raw_text

    def get_text(self):
        return self.text

    def apply_edit(self, edit: Edit):
        existing_lines = self.text.splitlines(keepends=True)
        lines_to_insert = edit.text_lines

        if edit.end is None:
            edit.end = edit.start

        if edit.end.line != edit.start.line:
            edit.end.column = 0

        new_lines = existing_lines[:edit.start.line] + \
                    ([existing_lines[edit.start.line][:edit.start.column]] if edit.start.line < len(
                        existing_lines) else []) + \
                    lines_to_insert + \
                    (([existing_lines[edit.end.line][edit.end.column:]] +
                      (existing_lines[edit.end.line + 1:] if edit.end.line + 1 < len(existing_lines) else []))
                     if edit.end.line < len(existing_lines) else [])

        self.text = "".join(new_lines)

    def mark_for_deletion(self):
        self.delete_me = True


def test_basic():
    yaml_view = YamlView(raw_text=nested_document, path=(), text_type=TextType.process, editor=FakeEditor())

    assert yaml_view.doc.raw_text == nested_document

    yaml_view.doc.parse_yaml()
    ch1 = yaml_view.create_child_view(path=("steps", "step2", "run"), editor=FakeEditor())

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
    assert ch1.doc.raw_text == expected


def open_tree():
    gen1 = YamlView(raw_text=nested_document, path=(), text_type=TextType.process, editor=FakeEditor())
    gen1.doc.parse_yaml()
    gen2 = gen1.create_child_view(path=("steps", "step2", "run"), editor=FakeEditor())
    gen2.doc.parse_yaml()
    gen3 = gen2.create_child_view(path=("steps", "step22", "run"), editor=FakeEditor())
    gen3.doc.parse_yaml()
    gen4 = gen3.create_child_view(path=("steps", "step221", "run"), editor=FakeEditor())
    gen4.doc.parse_yaml()
    gen5 = gen3.create_child_view(path=("steps", "step222", "run"), editor=FakeEditor())
    gen5.doc.parse_yaml()

    return gen1, gen2, gen3, gen4, gen5


def test_null_synchronization():
    gen1, gen2, gen3, gen4, gen5 = open_tree()

    assert gen4.attached_editor.get_text() == """steps:
- id: step2211
- id: step2212
"""
    gen4.attached_editor.set_text("""steps:
- id: step2211
- id: step2212""")
    gen4.fetch_from_editor()
    assert gen1.doc.raw_text == nested_document

    gen4.attached_editor.set_text("""steps:
- id: step2211
- id: step2212
""")
    gen4.fetch_from_editor()
    assert gen1.doc.raw_text == nested_document


def test_parse_error_synchronization():
    gen1, gen2, gen3, gen4, gen5 = open_tree()

    new_text = """steps:
  step221:
    run
      steps:
      - id: step2211
      - id: step2212
"""
    gen3.attached_editor.set_text(new_text)
    result = gen3.fetch_from_editor()
    assert result & Contents.ParseFail
    assert gen3.doc.raw_text == new_text
    assert gen3.attached_editor.locked


def test_ancestor_synchronization():
    gen1, gen2, gen3, gen4, gen5 = open_tree()

    assert gen4.attached_editor.get_text() == """steps:
- id: step2211
- id: step2212
"""
    gen4.attached_editor.set_text("""steps:
- id: step2211""")
    gen4.fetch_from_editor()
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
    assert gen1.doc.raw_text == expected


def test_child_synchronization():
    gen1, gen2, gen3, gen4, gen5 = open_tree()

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
    gen1.attached_editor.set_text(edited_document)
    gen1.fetch_from_editor()
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
    assert gen2.doc.raw_text == expected_gen2

    expected_gen4 = """steps:
- id: step2212  # <- other sibling deleted
"""
    assert gen4.doc.raw_text == expected_gen4


def test_child_removed():
    gen1, gen2, gen3, gen4, gen5 = open_tree()
    assert gen3.doc.raw_text == """steps:
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
    assert ("steps", "step221", "run") in gen3.children
    step221_editor = gen3.children[("steps", "step221", "run")].attached_editor

    new_text = """steps:
  step222:
    run:
      steps:
      - id: step2221
"""
    gen3.attached_editor.set_text(new_text)
    result = gen3.fetch_from_editor()
    assert gen3.doc.raw_text == new_text

    assert ("steps", "step221", "run") not in gen3.children
    assert step221_editor.delete_me

    assert not gen3.children["steps", "step222", "run"].attached_editor.delete_me
