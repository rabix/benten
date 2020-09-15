#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from lib import load, load_type_dicts

current_path = pathlib.Path(__file__).parent
schema_path = pathlib.Path(current_path, "../benten/000.package.data/")


def test_ebi_wf_cmsearch_multimodel():
    path = current_path / "cwl" / "ebi" / "workflows" / "cmsearch-multimodel-wf.cwl"
    doc = load(doc_path=path, type_dicts=load_type_dicts())

    step_symbols = next((symb for symb in doc.symbols if symb.name == "steps"), None)
    assert isinstance(step_symbols.children, list)

    cmsearch_symbol = next((symb for symb in step_symbols.children if symb.name == "cmsearch"), None)
    assert cmsearch_symbol.range.start.line == 33


def test_mass_wf_load():
    type_dicts = load_type_dicts()
    for wf_dir in ["ebi/workflows", "mgi/subworkflows", "mgi/pipelines", "cwl-v1.2"]:
        path = current_path / "cwl" / wf_dir
        for fname in path.glob("*.cwl"):
            _ = load(doc_path=fname, type_dicts=type_dicts)


def test_connections():
    path = current_path / "cwl" / "misc" / "wf-port-completer.cwl"
    doc = load(doc_path=path, type_dicts=load_type_dicts())

    assert len(doc.problems) == 0
