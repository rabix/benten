"""This class is responsible for

1. Identifying whether a CWL document is part of the SBG ecosystem and identifying it's version
2. Pushing a new app version to a SBG repository
3. Listing available versions of a workflow
4. Managing force push and pull operations
"""


file_not_pushed_suffix = "-local-edits"


class NotSBGApp:
    def __str__(self):
        return ""


class SBGAppInfo:
    def __init__(self, owner, project, name, version, local_edits):
        self.owner = owner
        self.project = project
        self.name = name
        self.version = version
        self.local_edits = local_edits

    def __str__(self):
        return "{} (v-{})".format(self.name, str(self.version) + ("**" if self.local_edits else ""))


# admin/sbg-public-data/salmon-index-0-9-1/12
#  user / project / app id / version
def get_app_info(app_id):
    info = NotSBGApp()
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


# class BaseAppManager:
#     def __init__(self, api):
#         self.api = api

