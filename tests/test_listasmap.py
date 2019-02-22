from benten.editing.listasmap import LAM, lom


def test_lab_basic():
    a_list = [
        {"id": "ln1", "line": "Billy left his home with a dollar in his pocket and a head full of dreams."},
        {"id": "ln2", "line": "He said somehow, some way, it's gotta get better than this."},
        {"id": "ln3", "line": "Patti packed her bags, left a note for her momma, she was just seventeen,"},
        {"id": "ln4", "line": "There were tears in her eyes when she kissed her little sister goodbye."},
        {             "line": "They held each other tight as they drove on through the night they were so excited."},
        {             "line": "We got just one shot of life, let's take it while we're still not afraid."}
    ]

    a_map = LAM(a_list, "id")

    assert len(a_map) == 4

    assert "ln2" in a_map
    assert a_map["ln4"]["line"] == "There were tears in her eyes when she kissed her little sister goodbye."

    assert len(a_map.errors) == 2

    another_list = [
        {
            ("class" if k == "id" else k): _v
            for k, _v in v.items()
        }
        for v in a_list
    ]

    b_map = LAM(another_list, "class")

    assert len(b_map) == 4

    assert "ln2" in b_map
    assert b_map["ln4"]["line"] == "There were tears in her eyes when she kissed her little sister goodbye."

    assert len(b_map.errors) == 2


def test_auto_switcher():
    a_list = [
        {"id": "ln1", "line": "I don't know why I love her like I do"},
        {"id": "ln2", "line": "All the changes you put me through"},
        {"id": "ln3", "line": "Take my money, my cigarettes"},
        {"id": "ln4", "line": "I haven't seen the worst of it yet"}
    ]

    a_map = {
        "ln5": "I want to know that you'll tell me",
        "ln6": "I love to stay",
        "ln7": "Take me to the river, drop me in the water",
        "ln8": "Take me to the river, dip me in the water"
    }

    assert type(lom(a_list)) == LAM
    assert type(lom(a_map)) == dict
