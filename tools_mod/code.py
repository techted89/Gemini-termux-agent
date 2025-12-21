import os
import sys
import shlex
import google.generativeai as genai
from helpers import run_command

def lint_python_file_task(filepath, linter="flake8"):
    """Runs a linter on a file."""
    cmd = f"{sys.executable} -m {linter} {shlex.quote(os.path.expanduser(filepath))}"
    try:
        result = run_command(cmd, shell=True, check_output=True, ignore_errors=True)
        return result if result.strip() else "No linting issues found."
    except Exception as e:
        return f"Lint Error: {e}"

def format_code_task(filepath, formatter="black"):
    """Runs a formatter on a file."""
    cmd = f"{sys.executable} -m {formatter} {shlex.quote(os.path.expanduser(filepath))}"
    try:
        result = run_command(cmd, shell=True, check_output=True, ignore_errors=True)
        return result or "Formatted successfully."
    except Exception as e:
        return f"Format Error: {e}"

def open_in_external_editor_task(filepath):
    try:
        cmd = f"termux-file-editor {shlex.quote(os.path.expanduser(filepath))}"
        run_command(cmd, shell=True)
        return f"Opened {filepath} in external editor."
    except Exception as e: return f"Error: {e}"

def launch_super_ide_task(project_path="."):
    """Launches Super-IDE for a project."""
    cmd = f"super-ide {shlex.quote(project_path)}"
    return run_command(cmd, shell=True, check_output=True) or "Launched Super-IDE."

def super_ide_project_task(name):
    """Creates a project in Super-IDE."""
    cmd = f"super-ide create {shlex.quote(name)}"
    return run_command(cmd, shell=True, check_output=True) or f"Created project {name}."

def super_ide_run_task(command):
    """Runs a command in Super-IDE context."""
    cmd = f"super-ide run {shlex.quote(command)}"
    return run_command(cmd, shell=True, check_output=True) or f"Ran: {command}"

definitions = {
    "launch_super_ide": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="launch_super_ide", description="Launch Super-IDE.", parameters={"type": "object", "properties": {"project_path": {"type": "string"}}, "required": []})]),
    "super_ide_project": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="super_ide_project", description="Create Super-IDE project.", parameters={"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]})]),
    "super_ide_run": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="super_ide_run", description="Run command in Super-IDE.", parameters={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]})]),
    "lint_python_file": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="lint_python_file", description="Lint Python", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
    "format_code": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="format_code", description="Format Python", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
    "open_in_external_editor": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="open_in_external_editor", description="Open Editor", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
}
