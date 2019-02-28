"""This class is meant to be mixed-in with CwlDoc so that it becomes SBG repo aware.
We operate at the level of CwlDoc since these operations and properties apply to inline
as well as base docs.

1. It will be able to say if the app has been registered on an SBG repo and extract it's version
2. It will be able to provide a list of versions for this app
3. It will be able to toggle the app id between pushed/not-pushed
    - todo: monitor if we need any clever manipulations on the not pushed id string to compare saves
4. It will be able to push and pull the app from the app repository. Pulling will return the raw
   cwl and someone else is responsible for inserting this as an edit
5. It will add a pushed/not pushed status to the class. These are blocking operations, so use with
   due care
"""
from sevenbridges import Api

file_not_pushed_suffix = "-local-edits"


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
    if app_id is not None:
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
        self.app_info = self.get_app_info()
        self.api: Api = api

    def get_app_info(self):
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
