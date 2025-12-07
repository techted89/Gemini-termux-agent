import bin.agent_tasks as tasks
from api import agentic_reason_and_act
from bin.tools.web import *
from bin.tools.memory import *
from bin.tools.automation.ui import *
from bin.tools.automation.browser import *
from bin.tools.automation.droidrun import *
from bin.tools.database import *
from bin.tools.git import *
from bin.tools.file_ops import *
from bin.tools.nlp import *
from bin.tools.cm import *
from bin.tools.core import *
from utils.database import (
    learn_directory,
    learn_url,
    learn_file_content,
    search_and_delete_knowledge,
    search_and_delete_history,
    get_available_metadata_sources,
)
from config import VPS_USER, VPS_IP, VPS_SSH_KEY_PATH
from utils.commands import user_confirm, run_command


def execute_tool(call, models):
    n = call.name
    a = call.args
    try:
        # Basic Tools
        if n == "google_search":
            return google_search(a["query"])
        if n == "learn_from_url_or_repo":
            return (
                learn_repo_task(a["url"])
                if a["url"].endswith(".git")
                else learn_url(a["url"])
            )
        if n == "read_file":
            return read_file_task(a["filepath"])
        if n == "execute_shell_command":
            # Handle vps_target logic
            if a.get("vps_target"):
                if not VPS_USER or not VPS_IP or not VPS_SSH_KEY_PATH:
                    return "Error: VPS config missing."
                ssh_cmd = a.get("ssh_command")
                full_cmd = f'ssh -i {VPS_SSH_KEY_PATH} {VPS_USER}@{VPS_IP} "{ssh_cmd}"'
                print(f"🤖 Running on VPS: {full_cmd}")
                if user_confirm("Approve VPS command?"):
                    return run_command(full_cmd, shell=True, check_output=True)
                return "Denied."
            return execute_shell_command(a["command"])
        if n == "create_file":
            return create_file_task(a["filepath"], a.get("content", ""))

        # Helper Tools
        if n == "lint_python_file":
            return lint_python_file_task(a["filepath"], a.get("linter", "flake8"))
        if n == "format_code":
            return format_code_task(a["filepath"], a.get("formatter", "black"))
        if n == "apply_sed":
            return apply_sed_task(
                a["filepath"], a["sed_expression"], a.get("in_place", True)
            )
        if n == "create_directory":
            return create_directory_task(a["directory_path"])
        if n == "list_directory_recursive":
            return list_directory_recursive_task(a["directory_path"])
        if n == "copy_file":
            return copy_file_task(a["source_path"], a["destination_path"])
        if n == "move_file":
            return move_file_task(a["source_path"], a["destination_path"])
        if n == "find_files":
            return find_files_task(
                a["directory_path"],
                a.get("name_pattern"),
                a.get("content_pattern"),
                a.get("max_depth", -1),
            )
        if n == "compress_path":
            return compress_path_task(
                a["source_path"], a["output_archive_path"], a.get("format", "zip")
            )
        if n == "decompress_archive":
            return decompress_archive_task(a["archive_path"], a["destination_path"])
        if n == "open_in_external_editor":
            return open_in_external_editor_task(a["filepath"])

        # UI Automation Tools
        if n == "open_app":
            return open_app(a.get("package_name"))
        if n == "tap_text":
            return tap_text(a["text"], a.get("timeout", 10))
        if n == "long_press_text":
            return long_press_text(
                a["text"], a.get("duration", 1.0), a.get("timeout", 10)
            )

        # Root-Based UI Automation Tools
        if n == "tap_screen":
            return tap_screen(a["x"], a["y"])
        if n == "swipe_screen":
            return swipe_screen(
                a["x1"], a["y1"], a["x2"], a["y2"], a.get("duration_ms", 300)
            )
        if n == "input_text":
            return input_text(a["text"])
        if n == "get_screen_analysis":
            return get_screen_analysis(
                a.get("output_path", "/sdcard/Pictures/screen_analysis.png")
            )
        if n == "extract_text_from_screen":
            return extract_text_from_screen()

        # Browser Automation Tools (Puppeteer)
        if n == "execute_puppeteer_script":
            return execute_puppeteer_script(
                a["url"],
                a.get("action", "screenshot"),
                a.get("output_file", "screenshot.png"),
            )

        # Droidrun Tools
        if n == "execute_droidrun_command":
            return execute_droidrun_command(a["command"])
        if n == "droidrun_portal_adb_command":
            return droidrun_portal_adb_command(
                a["portal_path"], a.get("action", "query"), a.get("data")
            )

        # Hugging Face Tools
        if n == "huggingface_sentence_similarity":
            return huggingface_sentence_similarity(
                a["source_sentence"], a["sentences_to_compare"]
            )

        # CM Tools
        if n == "execute_cm_command":
            return execute_cm_command(a["cm_command"])

        # Git Tools
        if n == "git_status":
            return git_status_task()
        if n == "git_pull":
            return git_pull_task(a.get("branch", "main"))
        if n == "git_push":
            return git_push_task(a.get("branch", "main"))
        if n == "git_branch":
            return git_branch_task(a.get("new_branch_name"))

        # Task Tools
        if n == "edit_file":
            return tasks.handle_edit_file(
                models["default"], a["filepath"], a["prompt"], a.get("save_as")
            )
        if n == "create_project":
            return tasks.handle_create_project(models["default"], a["prompt"])
        if n == "git_commit":
            return tasks.handle_git_commit(models["default"], a["prompt"])
        if n == "gh_issue":
            return tasks.handle_gh_issue(models["default"], a.get("repo"), a["prompt"])
        if n == "generate_image":
            return tasks.handle_image_generation(models["default"], a["prompt"])
        if n == "install":
            return tasks.handle_install(models["default"], a["prompt"])

        # DB Tools
        if n == "learn_file_content":
            return learn_file_content(a["filepath"], a.get("content"))
        if n == "learn_pdf_task":
            return learn_pdf_task(a["filepath"])
        if n == "learn_directory":
            return learn_directory(a["directory_path"], a.get("ignore_patterns"))
        if n == "learn_url":
            return learn_url(a["url"])
        if n == "search_and_delete_knowledge":
            return search_and_delete_knowledge(
                a.get("query"), a.get("source"), a.get("ids"), a.get("confirm")
            )
        if n == "search_and_delete_history":
            return search_and_delete_history(
                a.get("query"), a.get("role"), a.get("ids"), a.get("confirm")
            )
        if n == "get_available_metadata_sources":
            return get_available_metadata_sources()

        return f"Unknown: {n}"
    except Exception as e:
        return f"Tool Error: {e}"
