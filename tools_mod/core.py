import google.genai as genai
import os
from utils.commands import run_command, user_confirm

# --- Core Tools ---


def execute_shell_command(command):
    """Executes a shell command on the local system after user confirmation."""
    if user_confirm(f"Run: {command}?"):
        return run_command(command, shell=True, check_output=True)
    return "Denied."


def create_file_task(filepath, content=""):
    """Creates a new file at the specified path with optional content."""
    print(f"Tool: Running create_file_task(filepath='{filepath}')")
    try:
        expanded_filepath = os.path.expanduser(filepath)
        parent_dir = os.path.dirname(expanded_filepath)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        with open(expanded_filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Created file: {filepath}"
    except Exception as e:
        return f"Error creating file {filepath}: {e}"


def read_file_task(filepath):
    """Wrapper for reading a file to be called by the agent."""
    print(f'Tool: Running read_file_task(filepath="{filepath}")')
    try:
        filepath = os.path.expanduser(filepath)
        with open(filepath, "r") as f:
            content = f.read()
        return f"CONTEXT FILE ({filepath}):\n---\n{content}\n---"
    except Exception as e:
        return f"Error reading file {filepath}: {e}"


def install_packages(packages: list[str]):
    """Installs a list of packages using apt-get after user confirmation."""
    if not isinstance(packages, list):
        return "Error: a list of package names is required."

    package_str = " ".join(packages)
    cmd = f"sudo apt-get install -y {package_str}"

    if user_confirm(f"Run: {cmd}?"):
        return run_command(cmd, shell=True, check_output=True)
    return "Denied."


def tool_definitions():
    return [
        genai.types.Tool(
            function_declarations=[
                genai.types.FunctionDeclaration(
                    name="install_packages",
                    description="Install packages using apt-get",
                    parameters={
                        "type": "object",
                        "properties": {
                            "packages": {
                                "type": "array",
                                "items": {
                                    "type": "string"
                                }
                            }
                        },
                        "required": ["packages"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="execute_shell_command",
                    description="Run shell cmd",
                    parameters={
                        "type": "object",
                        "properties": {"command": {"type": "string"}},
                        "required": ["command"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="create_file",
                    description="Create File",
                    parameters={
                        "type": "object",
                        "properties": {
                            "filepath": {"type": "string"},
                            "content": {"type": "string"},
                        },
                        "required": ["filepath"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="read_file",
                    description="Read file",
                    parameters={
                        "type": "object",
                        "properties": {"filepath": {"type": "string"}},
                        "required": ["filepath"],
                    },
                ),
            ]
        )
    ]

library = {
    "execute_shell_command": execute_shell_command,
    "create_file": create_file_task,
    "read_file": read_file_task,
    "install_packages": install_packages,
}
