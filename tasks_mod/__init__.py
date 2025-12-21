from .vcs_tasks import handle_git_commit, handle_gh_issue
from .dev_tasks import (
    handle_edit_file,
    handle_create_project,
    handle_image_generation,
    handle_install,
)

_default_model = None


def set_default_model(model):
    global _default_model
    _default_model = model


def get_default_model():
    if _default_model is None:
        raise ValueError("Default model has not been set.")
    return _default_model
