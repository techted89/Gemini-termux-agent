from tools_mod.web import *
from tools_mod.memory import *
from tools_mod.automation.ui import *
from tools_mod.automation.browser import *
from tools_mod.automation.droidrun import *
from tools_mod.database import *
from tools_mod.git import *
from tools_mod.file_ops import *
from tools_mod.nlp import *
from tools_mod.cm import *
from tools_mod.core import *
from utils.commands import run_command


def execute_tool(function_call, models):
    """
    Executes a tool called by the model.
    """
    name = function_call.name
    args = function_call.args

    print(f"🛠️ Executing tool: {name}")

    try:
        # WEB
        if name == "search_web":
            return google_search(args["query"])
        # MEMORY
        elif name == "learn_directory":
            return learn_directory(args["directory_path"])
        elif name == "learn_repo_task":
            return learn_repo_task(args["repo_url"])
        elif name == "get_relevant_context":
            return get_relevant_context(args["query"])
        # AUTOMATION
        elif name == "open_app":
            return open_app(args["package_name"])
        elif name == "tap_text":
            return tap_text(args["text"], args.get("timeout", 10))
        elif name == "long_press_text":
            return long_press_text(
                args["text"], args.get("duration", 1.0), args.get("timeout", 10)
            )
        elif name == "extract_text_from_screen":
            return extract_text_from_screen()
        elif name == "execute_droidrun_command":
            return execute_droidrun_command(args["command"])
        elif name == "droidrun_portal_adb_command":
            return droidrun_portal_adb_command(args["command"])
        # GIT
        elif name == "git_status":
            return git_status_task()
        elif name == "git_pull":
            return git_pull_task(args.get("branch", "main"))
        elif name == "git_push":
            return git_push_task(args.get("branch", "main"))
        elif name == "git_branch":
             return git_branch_task(args.get("new_branch_name"))
        # FILE OPS
        elif name == "list_files":
            return list_directory_recursive_task(args.get("path", "."))
        elif name == "read_file":
            return read_file_task(args["path"])
        elif name == "write_file":
            return create_file_task(args["path"], args["content"])
        elif name == "edit_file":
             # This is tricky because `handle_edit_file` is in `tasks_mod` and requires user interaction/model.
             # If the agent calls it, we might need to route it differently or import it.
             # For now, let's assume the agent uses `apply_sed_task` or we implement a simple replace.
             # Or we can import `handle_edit_file` from `tasks_mod.dev_tasks` but it's interactive.
             # The memory implies `handle_edit_file` is a task.
             # If `edit_file` is a tool exposed to the agent, it should be non-interactive or handle it.
             # Let's check if `edit_file` is in `tool_definitions`.
             # Looking at `tools_mod/core.py` or others... `edit_file` wasn't in the grep list.
             # Maybe it was `apply_sed_task`?
             # Let's check `tools_mod/__init__.py` to see what tools are exposed.
             return f"Error: edit_file not directly supported in this mode. Use write_file to overwrite."
        elif name == "run_command":
             return execute_shell_command(args["command"])
        # NLP
        elif name == "huggingface_sentence_similarity":
            return "Error: huggingface_sentence_similarity is an internal tool."

        else:
            return f"Error: Unknown tool '{name}'"
    except Exception as e:
        return f"Error executing tool '{name}': {e}"
