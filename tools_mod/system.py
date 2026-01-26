import google.genai as genai
import shutil
import re
from utils.commands import run_command

def list_installed_packages_task(pattern=None):
    """
    Lists installed packages using dpkg (on Linux/Termux).
    """
    try:
        cmd = "dpkg -l"
        output = run_command(cmd, shell=True, check_output=True)
        if not output:
            return "Error listing packages."

        lines = output.splitlines()
        # Skip header lines
        packages = []
        for line in lines:
            if line.startswith("ii"):
                parts = line.split()
                if len(parts) >= 2:
                    pkg_name = parts[1]
                    if pattern:
                        if re.search(pattern, pkg_name):
                            packages.append(line)
                    else:
                        packages.append(line)

        if not packages:
            return "No packages found matching criteria."

        return "\n".join(packages[:100]) + ("\n... (truncated)" if len(packages) > 100 else "")
    except Exception as e:
        return f"Error: {e}"

def check_tool_installed_task(tool_name):
    """
    Checks if a CLI tool is installed using the shell.
    """
    if not re.match(r"^[a-zA-Z0-9_-]+$", tool_name):
        return "Invalid tool name."

    try:
        # Use shell execution to check for tool presence
        cmd = f"command -v {tool_name}"
        path = run_command(cmd, shell=True, check_output=True)
        if path:
            return f"Tool '{tool_name}' is installed at {path}"
        else:
            return f"Tool '{tool_name}' is NOT installed."
    except Exception:
        # If command fails (exit code != 0), it's not found
        return f"Tool '{tool_name}' is NOT installed."

def tool_definitions():
    return [
        genai.types.Tool(
            function_declarations=[
                genai.types.FunctionDeclaration(
                    name="list_installed_packages",
                    description="Lists installed system packages (optionally matching a pattern).",
                    parameters={
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string", "description": "Regex pattern to filter package names"}
                        },
                        "required": [],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="check_tool_installed",
                    description="Checks if a specific CLI tool is available.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "tool_name": {"type": "string", "description": "Name of the tool to check"}
                        },
                        "required": ["tool_name"],
                    },
                ),
            ]
        )
    ]

library = {
    "list_installed_packages": list_installed_packages_task,
    "check_tool_installed": check_tool_installed_task,
}
