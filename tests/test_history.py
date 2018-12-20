import pytest
import pathlib

import benten.editing.history as bhistory

current_path = pathlib.Path(__file__).parent


def test_history():
    hist = bhistory.History("My first words")

    with pytest.raises(bhistory.OutOfHistory):
        hist.undo()

    with pytest.raises(bhistory.OutOfHistory):
        hist.redo()

    hist.append("My next words")

    assert hist.undo() == "My first words"
    assert hist.redo() == "My next words"
    assert hist.undo() == "My first words"

    hist.append("My new next words")
    assert hist.undo() == "My first words"

    with pytest.raises(bhistory.OutOfHistory):
        hist.undo()

    assert hist.redo() == "My new next words"

    with pytest.raises(bhistory.OutOfHistory):
        hist.redo()
