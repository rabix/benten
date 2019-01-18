import pathlib

import benten
import benten.langserver.default_templates as def_tplt


class Configuration:
    def __init__(self, config_path: pathlib.Path):
        def_tplt.copy_cwl_templates_to_config_directory_as_needed()
        self.cwl_templates = def_tplt.default_templates
        for label, data in self.cwl_templates.items():
            p = pathlib.Path(benten.template_dir, data["file"])
            if p.exists():
                with open(p, "r") as f:
                    data["cwl"] = f.read()
