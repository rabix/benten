"""This class is responsible for

1. Identifying whether a CWL document is part of the SBG ecosystem and identifying it's version
2. Pushing a new app version to a SBG repository
3. Listing available versions of a workflow
4. Managing force push and pull operations
"""


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
                v = int(parts[-1])
                info = {
                    "owner": parts[0],
                    "project": parts[1],
                    "name": parts[2],
                    "version": v
                }
            except ValueError:
                pass

    return info


class BaseAppManager:
    def __init__(self, api):
        self.api = api

