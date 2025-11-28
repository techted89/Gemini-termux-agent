from tasks_mod.vcs_tasks import handle_git_commit, handle_gh_issue
from tasks_mod.dev_tasks import handle_image_generation, handle_edit_file, handle_create_project, handle_install

default_model = None

def set_default_model(model):
    global default_model
    default_model = model
