"""This handles
1. Pulling version information from the SBG repository
2. Manipulating the "sbg:id" tag in response to local edits, pushes and retrieval of versions

Algorithm of note:

Editing a view of a document marks it and any ancestor documents also as edited. We need to walk
back up the ancestor chain doing this. We do all this programmatically




For this reason we can use a

As a result we can use a fast algorithm


"""
from sevenbridges import Api

from ..editing.rootyamlview import RootYamlView, YamlView

file_not_pushed_suffix = "-local-edits"


def mark_with_local_edits(raw_text):
    lines = raw_text.splitlines(keepends=True)
    for n, line in enumerate(lines):
        if line.startswith("sbg:id: "):
            if not line.strip("\n").endswith(file_not_pushed_suffix):
                lines[n] = lines[n].rstrip() + file_not_pushed_suffix + "\n"
            break
    return "".join(lines)



def strip_local_edits_suffix(path_str):
    if path_str.endswith(file_not_pushed_suffix):
        return path_str[:-len(file_not_pushed_suffix)]
    else:
        return path_str


# lets see how far we can get with a heuristic
def change_or_add_sbg_repo_tag(raw_text, new_id):
    lines = raw_text.splitlines(keepends=True)
    for n, line in enumerate(lines):
        if line.startswith("sbg:id: "):
            lines[n] = "sbg:id: " + new_id + "\n"
            break
    else:
        lines.append("sbg:id: " + new_id + "\n")
    return "".join(lines)


def propagate_local_edits_tag(view: YamlView, new_id=None):
    """Edits to a registered app should be marked with a prefix disconnecting it from the
    repository. These "local change" tags should propagate to all ancestors."""
    if "sbg:id" in view.yaml and \
            view.yaml["sbg:id"].endswith(file_not_pushed_suffix) and \
            new_id is None:
        return

    base = view.root()
    new_lines = _propagate_local_edits_tag(base.raw_lines, base.yaml, view.inline_path, new_id)
    base.set_raw_text("".join(new_lines))
    base.synchronize_text()


def _propagate_local_edits_tag(lines, obj, inline_path, new_id):
    if len(inline_path):  # Still a ways to go
        if "sbg:id" in obj:
            sbg_id_v = obj["sbg:id"]
            if not sbg_id_v.endswith(file_not_pushed_suffix):
                lines[sbg_id_v.start.line] = lines[sbg_id_v.start.line].rstrip() + file_not_pushed_suffix + "\n"
        return _propagate_local_edits_tag(lines, obj[inline_path[0]], inline_path[1:], new_id)
    else:
        if "sbg:id" in obj:
            sbg_id_v = obj["sbg:id"]
            if new_id is not None:
                lines[sbg_id_v.start.line] = lines[sbg_id_v.start.line][:sbg_id_v.start.column] + new_id + "\n"
            else:
                if not sbg_id_v.endswith(file_not_pushed_suffix):
                    lines[sbg_id_v.start.line] = lines[sbg_id_v.start.line].rstrip() + file_not_pushed_suffix + "\n"
        elif new_id is not None:
            new_line = " " * obj.start.column + "sbg:id: " + new_id + "\n"
            lines = lines[:obj.end.line] + [new_line] + lines[obj.end.line:]
        return lines


class SBGAppInfo:
    def __init__(self, owner, project, name, version, local_edits):
        self.owner = owner
        self.project = project
        self.name = name
        self.version = version
        self.local_edits = local_edits

    def get_id_str(self):
        return "/".join([self.owner, self.project, self.name, self.version] +
                        ([file_not_pushed_suffix] if self.local_edits else []))

    def get_app_base_path(self):
        return "/".join([self.owner, self.project, self.name])

    def get_app_path_with_version(self):
        return "/".join([self.owner, self.project, self.name, self.version])

    def __str__(self):
        return "{} (v:{})".format(self.name, str(self.version) + ("*" if self.local_edits else ""))


# We provide this for current standalone usage but will refactor later ...
# admin/sbg-public-data/salmon-index-0-9-1/12
#  user / project / app id / version
def get_app_info(app_id):
    info = None
    if isinstance(app_id, str):
        parts = app_id.split("/")
        if len(parts) != 4:
            pass
        else:
            try:
                local_edits = False
                _version_str = parts[-1]
                if parts[-1].endswith(file_not_pushed_suffix):
                    local_edits = True
                    _version_str = parts[-1][:-len(file_not_pushed_suffix)]

                v = int(_version_str)
                info = SBGAppInfo(
                    owner=parts[0],
                    project=parts[1],
                    name=parts[2],
                    version=v,
                    local_edits=local_edits)
            except ValueError:
                pass

    return info


def get_id_line(cwl_lines):
    return next((l for l in cwl_lines if l.startswith("id:")), None)


class NotRegisteredWithSBG(Exception):
    def __str__(self):
        return "This app is not registered in the SBG repo"


class VersionMixin:
    def __init__(self, *args, api: Api=None, **kwargs):
        # https://stackoverflow.com/a/34998801/2512851
        # This mixin expects access to CwlDoc like properties at initialization
        # We call the ancestor first. This will either be CwlDoc, or other mixins, which, in turn
        # call their ancestors first, which will result in CwlDoc being called first.
        super(VersionMixin, self).__init__(*args, **kwargs)
        self.api = None
#        self.app_info = None

    def set_api(self, api: Api=None):
        self.api = api

    @property
    def app_info(self):
        id_line = get_id_line(self.cwl_lines)
        if id_line is None:
            return None
        return get_app_info(id_line[3:].strip())

    def get_app_revisions(self, *args):
        if self.app_info is None:
            raise NotRegisteredWithSBG()
        else:
            most_recent_app = self.api.apps.get(id=self.app_info.get_app_base_path())
            return most_recent_app.raw["sbg:revisionsInfo"]

    def mark_as_locally_edited(self, flag):
        if self.app_info is None:
            return None

        self.app_info.local_edits = flag
        return self.app_info.get_id_str()
