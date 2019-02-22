"""Some CWL fields allow us to use a list or a map. In such a case the list always has to
have a particular field (usually "id" or "class") that is the key value. Often we'd like to
navigate such lists just like a map"""

error_key_prefix = "missing key field"


def lom(obj: (list, dict), key_field: str="id"):
    if isinstance(obj, dict):
        return obj
    else:
        return LAM(obj, key_field)


class LAM(dict):
    def __init__(self, obj: list, key_field: str="id"):
        secret_missing_key = "there is no CWL field that looks like this, and it can safely be used"
        self.errors = []

        def _add_error_line(ln):
            self.errors += [ln]
            return secret_missing_key

        dict.__init__(self, {
            (v.get(key_field) or _add_error_line(v)): v
            for v in obj
        })

        if secret_missing_key in self:
            self.pop(secret_missing_key)
