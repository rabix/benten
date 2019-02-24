"""Load a JSON file, strip out insessential SBG tags and convert it into YAML. Change the
base file name if needed."""
from ..editing.lineloader import yaml, Loader


def _strip_sbg_tags(node):
    if isinstance(node, dict):
        return {
            k: _strip_sbg_tags(v)
            for k, v in node.items()
            if k[:4] != "sbg:"
        }
    elif isinstance(node, list):
        return [
            _strip_sbg_tags(n)
            for n in node
        ]
    else:
        return node


def import_json(raw_json, strip_sbg_tags=True):
    d = yaml.load(raw_json, Loader=Loader)
    if strip_sbg_tags:
        d = _strip_sbg_tags(d)
    return d


class JsonMixin:
    def __init__(self, *args, raw_json=None, strip_sbg_tags=True, new_path=None, **kwargs):
        # This mixin is special. It should be the first mixin because it's kind of a bouncer,
        # tossing out JSON and replacing it with YAML. In any case, it wants to do its processing
        # first, before letting other classes have a go. It does all it does in the initializer
        # new_path has to be supplied.
        if raw_json is not None:
            if new_path is None:
                raise RuntimeError("New CWL filename after conversion must be provided")
            kwargs["raw_cwl"] = yaml.safe_dump(import_json(raw_json, strip_sbg_tags=strip_sbg_tags))
            kwargs["path"] = new_path

        super(JsonMixin, self).__init__(*args, **kwargs)

    @staticmethod
    def detect_cwl_format(text):
        if text.lstrip():
            if text.lstrip()[0] == "{":
                return "json"

        return "yaml"
