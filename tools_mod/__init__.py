import google.generativeai as genai
from . import file_system, git, code, web, android, system
import db
import config
from config import VPS_USER, VPS_IP, VPS_SSH_KEY_PATH
from helpers import user_confirm, run_command

# Combine definitions
tool_definitions = {}
tool_definitions.update(file_system.definitions)
tool_definitions.update(git.definitions)
tool_definitions.update(code.definitions)
tool_definitions.update(web.definitions)
tool_definitions.update(android.definitions)
tool_definitions.update(system.definitions)

# DB Tool Definitions
db_definitions = {
    "learn_file_content": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="learn_file_content", description="Learn File", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
    "learn_directory": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="learn_directory", description="Learn Dir", parameters={"type": "object", "properties": {"directory_path": {"type": "string"}, "ignore_patterns": {"type": "array", "items": {"type": "string"}}}, "required": ["directory_path"]})]),
    "learn_url": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="learn_url", description="Learn URL", parameters={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]})]),
    "search_and_delete_knowledge": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="search_and_delete_knowledge", description="Search/Del Knowledge", parameters={"type": "object", "properties": {"query": {"type": "string"}, "source": {"type": "string"}, "ids": {"type": "array", "items": {"type": "string"}}, "confirm": {"type": "boolean"}}, "required": []})]),
    "search_and_delete_history": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="search_and_delete_history", description="Search/Del History", parameters={"type": "object", "properties": {"query": {"type": "string"}, "role": {"type": "string"}, "ids": {"type": "array", "items": {"type": "string"}}, "confirm": {"type": "boolean"}}, "required": []})]),
    "get_available_metadata_sources": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="get_available_metadata_sources", description="Get available metadata sources for filtering.", parameters={"type": "object", "properties": {}})])
}
tool_definitions.update(db_definitions)

# Task Tool Definitions
task_definitions = {
    "edit_file": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="edit_file", description="Edit file", parameters={"type": "object", "properties": {"filepath": {"type": "string"}, "prompt": {"type": "string"}, "save_as": {"type": "string"}}, "required": ["filepath", "prompt"]})]),
    "create_project": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="create_project", description="Create project", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
    "git_commit": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="git_commit", description="Git commit", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
    "gh_issue": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="gh_issue", description="GitHub Issue", parameters={"type": "object", "properties": {"repo": {"type": "string"}, "prompt": {"type": "string"}}, "required": ["prompt"]})]),
    "generate_image": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="generate_image", description="Generate Image", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
    "install": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="install", description="Install Package", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
}
tool_definitions.update(task_definitions)

# Agentic Tool Definitions
agentic_definitions = {
    "agentic_plan": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="agentic_plan", description="Create Plan", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
    "agentic_reason": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="agentic_reason", description="Reasoning", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
    "agentic_execute": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="agentic_execute", description="Execute Action", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
}
tool_definitions.update(agentic_definitions)


def execute_tool(call, models):
    import tasks # Lazy import
    from api import agentic_plan, agentic_reason, agentic_execute

    n = call.name; a = call.args
    try:
        # File System
        if n == "read_file": return file_system.read_file_task(a["filepath"])
        if n == "create_file": return file_system.create_file_task(a["filepath"], a.get("content", ""))
        if n == "apply_sed": return file_system.apply_sed_task(a["filepath"], a["sed_expression"], a.get("in_place", True))
        if n == "create_directory": return file_system.create_directory_task(a["directory_path"])
        if n == "list_directory_recursive": return file_system.list_directory_recursive_task(a["directory_path"])
        if n == "copy_file": return file_system.copy_file_task(a["source_path"], a["destination_path"])
        if n == "move_file": return file_system.move_file_task(a["source_path"], a["destination_path"])
        if n == "find_files": return file_system.find_files_task(a["directory_path"], a.get("name_pattern"), a.get("content_pattern"), a.get("max_depth", -1))
        if n == "compress_path": return file_system.compress_path_task(a["source_path"], a["output_archive_path"], a.get("format", "zip"))
        if n == "decompress_archive": return file_system.decompress_archive_task(a["archive_path"], a["destination_path"])

        # Code
        if n == "lint_python_file": return code.lint_python_file_task(a["filepath"], a.get("linter", "flake8"))
        if n == "format_code": return code.format_code_task(a["filepath"], a.get("formatter", "black"))
        if n == "open_in_external_editor": return code.open_in_external_editor_task(a["filepath"])

        # Web / Learning
        if n == "google_search": return web.google_search(a["query"])
        if n == "learn_from_url_or_repo": return web.learn_repo_task(a["url"]) if a["url"].endswith(".git") else db.learn_url(a["url"]) # Modified to use db.learn_url for non-git
        if n == "learn_pdf_task": return web.learn_pdf_task(a["filepath"])
        if n == "execute_puppeteer_script": return web.execute_puppeteer_script(a["url"], a.get("action", "screenshot"), a.get("output_file", "screenshot.png"))
        if n == "huggingface_sentence_similarity": return web.huggingface_sentence_similarity(a["source_sentence"], a["sentences_to_compare"])

        # Git
        if n == "git_status": return git.git_status_task()
        if n == "git_pull": return git.git_pull_task(a.get("branch", "main"))
        if n == "git_push": return git.git_push_task(a.get("branch", "main"))
        if n == "git_branch": return git.git_branch_task(a.get("new_branch_name"))

        # System
        if n == "execute_shell_command":
            if a.get("vps_target"):
                 if not VPS_USER or not VPS_IP or not VPS_SSH_KEY_PATH: return "Error: VPS config missing."
                 ssh_cmd = a.get("ssh_command")
                 full_cmd = f'ssh -i {VPS_SSH_KEY_PATH} {VPS_USER}@{VPS_IP} "{ssh_cmd}"'
                 print(f"🤖 Running on VPS: {full_cmd}")
                 if user_confirm("Approve VPS command?"): return run_command(full_cmd, shell=True, check_output=True)
                 return "Denied."
            return system.execute_shell_command(a["command"])
        if n == "execute_cm_command": return system.execute_cm_command(a["cm_command"])

        # Android
        if n == "open_gemini_app": return android.open_gemini_app_task(a.get("package_name", "com.google.android.apps.bard"))
        if n == "android_ui_find_and_tap_text": return android.android_ui_find_and_tap_text(a["text"], a.get("timeout", 10))
        if n == "android_ui_long_press_text": return android.android_ui_long_press_text(a["text"], a.get("duration", 1.0), a.get("timeout", 10))
        if n == "tap_screen": return android.tap_screen(a["x"], a["y"])
        if n == "swipe_screen": return android.swipe_screen(a["x1"], a["y1"], a["x2"], a["y2"], a.get("duration_ms", 300))
        if n == "input_text": return android.input_text(a["text"])
        if n == "get_screen_analysis": return android.get_screen_analysis(a.get("output_path", "/sdcard/Pictures/screen_analysis.png"))
        if n == "extract_text_from_screen": return android.extract_text_from_screen()
        if n == "execute_droidrun_command": return android.execute_droidrun_command(a["command"])
        if n == "droidrun_portal_adb_command": return android.droidrun_portal_adb_command(a["portal_path"], a.get("action", "query"), a.get("data"))

        # Tasks
        if n == "edit_file": return tasks.handle_edit_file(models['default'], a["filepath"], a["prompt"], a.get("save_as"))
        if n == "create_project": return tasks.handle_create_project(models['default'], a["prompt"])
        if n == "git_commit": return tasks.handle_git_commit(models['default'], a["prompt"])
        if n == "gh_issue": return tasks.handle_gh_issue(models['default'], a.get("repo"), a["prompt"])
        if n == "generate_image": return tasks.handle_image_generation(models['default'], a["prompt"])
        if n == "install": return tasks.handle_install(models['default'], a["prompt"])

        # DB
        if n == "learn_file_content": return db.learn_file_content(a["filepath"], a.get("content"))
        if n == "learn_directory": return db.learn_directory(a["directory_path"], a.get("ignore_patterns"))
        if n == "learn_url": return db.learn_url(a["url"])
        if n == "search_and_delete_knowledge": return db.search_and_delete_knowledge(a.get("query"), a.get("source"), a.get("ids"), a.get("confirm"))
        if n == "search_and_delete_history": return db.search_and_delete_history(a.get("query"), a.get("role"), a.get("ids"), a.get("confirm"))
        if n == "get_available_metadata_sources": return db.get_available_metadata_sources()

        # Agentic
        if n == "agentic_plan": return agentic_plan(a["prompt"], tools=list(tool_definitions.values()))
        if n == "agentic_reason": return agentic_reason(a["prompt"], models['default'])
        if n == "agentic_execute": return agentic_execute(a["prompt"], models['default'])

        return f"Unknown: {n}"
    except Exception as e: return f"Tool Error: {e}"
