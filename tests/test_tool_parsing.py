#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from lib import load, load_type_dicts

current_path = pathlib.Path(__file__).parent


def test_mass_tool_load():
    type_dicts = load_type_dicts()
    for wf_dir in ["ebi/tools", "mgi/tools"]:
        path = current_path / "cwl" / wf_dir
        for fname in path.glob("*.cwl"):
            _ = load(doc_path=fname, type_dicts=type_dicts)


def test_troublesome_tool_load():
    type_dicts = load_type_dicts()
    path = current_path / "cwl" / "misc"
    for fname in path.glob("*.cwl"):
        _ = load(doc_path=fname, type_dicts=type_dicts)
