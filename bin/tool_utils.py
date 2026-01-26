from tools_mod.web import *
from tools_mod.memory import *
from tools_mod.database import *
from tools_mod.git import *
from tools_mod.file_ops import *
from tools_mod.nlp import *
# from tools_mod.cm import * # cm module might not exist in this environment, skipping
from tools_mod.core import *
from utils.commands import run_command


def execute_tool(function_call, models):
    """
    Executes a tool called by the model.
    """
    name = function_call.name
    args = function_call.args
    print(f"🛠️ Executing tool: {name}")

    def get_arg(keys):
        """Helper to get argument from a list of possible keys."""
        return next((args[k] for k in keys if k in args), None)

    try:
        # WEB
        if name == "search_web":
            return google_search(get_arg(['query', 'q']))
        # MEMORY
        elif name == "learn_directory":
            return learn_directory(get_arg(['directory_path', 'path', 'directory']))
        elif name == "learn_repo_task":
            return learn_repo_task(get_arg(['repo_url', 'url']))
        elif name == "get_relevant_context":
            return get_relevant_context(get_arg(['query']))
        
        # GIT
        elif name == "git_status":
            return git_status_task()
        elif name == "git_pull":
            return git_pull_task(get_arg(['branch']) or "main")
        elif name == "git_push":
            return git_push_task(get_arg(['branch']) or "main")
        elif name == "git_branch":
             return git_branch_task(get_arg(['new_branch_name', 'name']))

        # FILE OPS
        elif name == "list_files":
            return list_directory_recursive_task(get_arg(['path', 'directory', 'folder']) or ".")
        elif name == "read_file":
            return read_file_task(get_arg(['path', 'filepath', 'filename']))
        elif name == "write_file":
            # Using save_to_file_task for consistency with file_ops tools
            return save_to_file_task(get_arg(['path', 'filepath', 'filename']), get_arg(['content', 'data']))

        # CORE / RUN COMMAND
        elif name == "run_command":
             return execute_shell_command(get_arg(['command', 'cmd']))

        # NLP
        elif name == "huggingface_sentence_similarity":
            return "Error: huggingface_sentence_similarity is an internal tool."

        else:
            return f"Error: Unknown tool '{name}'"
    except Exception as e:
        return f"Error executing tool '{name}': {e}"
