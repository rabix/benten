import sevenbridges.errors as sbgerr

from ..sbg.versionmanagement import strip_local_edits_suffix

import logging
logger = logging.getLogger(__name__)
logging.getLogger("sevenbridges.http.client").propagate = False
logging.getLogger("urllib3.connectionpool").propagate = False

sbgerr.SbgError.__str__ = lambda x: str(x.message)
# Monkey patch until https://github.com/sbg/sevenbridges-python/pull/119 is resolved


def valid(app_path):
    parts = app_path.split("/")
    return len(parts) == 3


# "sbg:id": "kghose/rabix-web-demo/clt1/0"
def push(api, yaml, commit_message, app_path=None):
    if yaml is None:
        error_message = "Can not push malformed CWL document"
        logger.debug(error_message)
        raise RuntimeError(error_message)

    if app_path is None:
        if "sbg:id" not in yaml:
            raise RuntimeError("This app has not been registered in the repository.\n"
                               "Please pass an app path (user/project/appid) to register.")
        else:
            app_path = strip_local_edits_suffix(yaml["sbg:id"])
    else:
        if not valid(app_path):
            raise RuntimeError("App path needs to be in the form user/project/app_id")

    yaml["sbg:revisionNotes"] = commit_message
    try:
        app = api.apps.get(app_path)
        logger.debug("Creating revised app: {}".format(app_path))
        return api.apps.create_revision(
            id=app_path,
            raw=yaml,
            revision=app.revision + 1
        )
    except sbgerr.NotFound:
        logger.debug("Creating new app: {}".format(app_path))
        return api.apps.install_app(
            id=app_path,
            raw=yaml
        )
