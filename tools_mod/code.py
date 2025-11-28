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

definitions = {
    "lint_python_file": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="lint_python_file", description="Lint Python", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
    "format_code": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="format_code", description="Format Python", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
    "open_in_external_editor": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="open_in_external_editor", description="Open Editor", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
}
