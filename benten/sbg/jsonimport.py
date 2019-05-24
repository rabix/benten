"""Load a JSON file, strip out insessential SBG tags and convert it into YAML. Change the
base file name if needed."""
#  Copyright (c) 2019 Seven Bridges. See LICENSE

import pathlib

from .utils import _strip_sbg_tags
from ..editing.lineloader import yaml, Loader, ParserError, DocumentError

import logging
logger = logging.getLogger(__name__)


def if_json_convert_to_yaml_and_save(path: pathlib.Path, strip_sbg_tags=True):
    text = path.open().read()
    if text_format(text) == "json":
        logger.debug("Converting json to yaml ...")
        new_path = pathlib.Path(path.parent, path.name + ".cwl")
        with open(new_path, "w") as f:
            f.write(yaml.safe_dump(import_json(text, strip_sbg_tags=strip_sbg_tags)))
        return new_path
    else:
        return path


def text_format(text: str):
    if text.lstrip():
        if text.lstrip()[0] == "{":
            return "json"
    return "yaml"


def import_json(raw_json, strip_sbg_tags=True):
    d = yaml.load(raw_json, Loader=Loader)
    if strip_sbg_tags:
        d = _strip_sbg_tags(d)
    return d
