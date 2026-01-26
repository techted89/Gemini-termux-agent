import google.genai as genai
import shlex
from utils.commands import run_command


def git_status_task():
    return (
        run_command("git status --short", shell=True, check_output=True)
        or "Working tree clean."
    )


def git_pull_task(branch="main"):
    sanitized_branch = shlex.quote(branch)
    return run_command(f"git pull origin {sanitized_branch}", shell=True, check_output=True)


def git_push_task(branch="main"):
    sanitized_branch = shlex.quote(branch)
    return run_command(f"git push origin {sanitized_branch}", shell=True, check_output=True)


def git_branch_task(new_branch_name=None):
    if new_branch_name:
        sanitized_name = shlex.quote(new_branch_name)
        return run_command(
            f"git checkout -b {sanitized_name}", shell=True, check_output=True
        )
    return run_command("git branch", shell=True, check_output=True)

def git_commit_task(message):
    sanitized_msg = shlex.quote(message)
    # Uses -am to add modified files automatically.
    return run_command(f"git commit -am {sanitized_msg}", shell=True, check_output=True)

def git_diff_task():
    return run_command("git diff", shell=True, check_output=True)

def git_log_task(limit=5):
    return run_command(f"git log -n {limit}", shell=True, check_output=True)

def git_add_task(files):
    sanitized_files = shlex.quote(files)
    return run_command(f"git add {sanitized_files}", shell=True, check_output=True)

def tool_definitions():
    return [
        genai.types.Tool(
            function_declarations=[
                genai.types.FunctionDeclaration(
                    name="git_status",
                    description="Git Status",
                    parameters={"type": "object", "properties": {}},
                ),
                genai.types.FunctionDeclaration(
                    name="git_pull",
                    description="Git Pull",
                    parameters={
                        "type": "object",
                        "properties": {"branch": {"type": "string"}},
                        "required": [],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="git_push",
                    description="Git Push",
                    parameters={
                        "type": "object",
                        "properties": {"branch": {"type": "string"}},
                        "required": [],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="git_branch",
                    description="Git Branch",
                    parameters={
                        "type": "object",
                        "properties": {"new_branch_name": {"type": "string"}},
                        "required": [],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="git_commit",
                    description="Git Commit (adds modified files)",
                    parameters={
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                        "required": ["message"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="git_diff",
                    description="Git Diff",
                    parameters={"type": "object", "properties": {}},
                ),
                genai.types.FunctionDeclaration(
                    name="git_log",
                    description="Git Log",
                    parameters={
                        "type": "object",
                        "properties": {"limit": {"type": "integer"}},
                        "required": [],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="git_add",
                    description="Git Add",
                    parameters={
                        "type": "object",
                        "properties": {"files": {"type": "string"}},
                        "required": ["files"],
                    },
                ),
            ]
        )
    ]

library = {
    "git_status": git_status_task,
    "git_pull": git_pull_task,
    "git_push": git_push_task,
    "git_branch": git_branch_task,
    "git_commit": git_commit_task,
    "git_diff": git_diff_task,
    "git_log": git_log_task,
    "git_add": git_add_task,
}
