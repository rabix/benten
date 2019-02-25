"""Some useful functions we use in several places"""

# We use this for the inputs/outputs of the subprocess and we ignore ports with no "id"
# Having no "id" is an error, but in the subworkflow, and we don't bother to report that
def dictify(obj: (list, dict)):
    if isinstance(obj, dict):
        return obj
    else:
        return {v.get("id"): v for v in obj if v.get("id") is not None}


def iter_scalar_or_list(obj: (list, str)):
    if isinstance(obj, list):
        return obj
    else:
        return [obj]
