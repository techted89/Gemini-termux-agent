import shlex
import google.generativeai as genai
from config import VPS_USER, VPS_IP, VPS_SSH_KEY_PATH
from helpers import run_command, user_confirm

def execute_shell_command(cmd):
    """Executes a shell command on the local system after user confirmation."""
    if user_confirm(f"Run: {cmd}?"):
        return run_command(cmd, shell=True, check_output=True)
    return "Denied."

def execute_cm_command(cm_command):
    """Executes a Collective Mind (CM) command."""
    print(f"Tool: Running execute_cm_command(cm_command={str(cm_command)})")
    full_cmd = f"cm {shlex.quote(cm_command)}"
    if user_confirm(f"Run CM command: {full_cmd}?"):
        try:
            result = run_command(full_cmd, shell=True, check_output=True)
            return result
        except Exception as e:
            return f"Error executing CM command: {e}"
    return "Denied."

definitions = {
    "execute_shell_command": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="execute_shell_command", description="Run shell cmd", parameters={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]})]),
    "execute_cm_command": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="execute_cm_command", description="Executes a Collective Mind (CM) command.", parameters={"type": "object", "properties": {"cm_command": {"type": "string"}}, "required": ["cm_command"]})]),
}
