import google.genai as genai
from utils.commands import run_command


def git_status_task():
    return (
        run_command("git status --short", shell=True, check_output=True)
        or "Working tree clean."
    )


def git_pull_task(branch="main"):
    return run_command(f"git pull origin {branch}", shell=True, check_output=True)


def git_push_task(branch="main"):
    return run_command(f"git push origin {branch}", shell=True, check_output=True)


def git_branch_task(new_branch_name=None):
    if new_branch_name:
        return run_command(
            f"git checkout -b {new_branch_name}", shell=True, check_output=True
        )
    return run_command("git branch", shell=True, check_output=True)


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
            ]
        )
    ]

library = {
    "git_status": git_status_task,
    "git_pull": git_pull_task,
    "git_push": git_push_task,
    "git_branch": git_branch_task,
}
