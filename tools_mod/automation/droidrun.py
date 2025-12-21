import shlex
import json
import google.generativeai as genai
from utils.commands import run_command, user_confirm


def execute_droidrun_command(command):
    """Executes a Droidrun CLI command."""
    print(f'Tool: Running execute_droidrun_command(command="{command}")')
    full_cmd = f"droidrun {shlex.quote(command)}"
    if user_confirm(f"Run Droidrun command: {full_cmd}?"):
        try:
            result = run_command(full_cmd, shell=True, check_output=True)
            return result
        except Exception as e:
            return f"Error executing Droidrun command: {e}"
    return "Denied."


def droidrun_portal_adb_command(portal_path, action="query", data=None):
    """
    Interacts with the Droidrun-Portal content provider via ADB shell.

    This tool allows for querying device state or inserting data/commands.
    The output is parsed as JSON if possible for structured data access.

    Args:
        portal_path (str): The specific data path in the portal.
            Examples:
            - 'a11y_tree': Fetches the full accessibility tree as JSON.
            - 'state': Gets the current device state (screen on/off, etc.).
            - 'ping': Checks if the Droidrun portal is responsive.
            - 'keyboard/input': Sends text to the keyboard.
            - 'keyboard/key': Sends a key press event.
        action (str, optional): The action to perform. Must be either 'query'
            (to retrieve data) or 'insert' (to send data).
            Defaults to "query".
        data (dict, optional): A dictionary of data to be sent with an 'insert'
            action. The keys are the data fields and values are the content.
            Examples:
            - For 'keyboard/input': {'base64_text': 'SGVsbG8gV29ybGQ='} (Base64 for "Hello World")
            - For 'keyboard/key': {'key_code': 66} (Key code for ENTER)

    Returns:
        dict or str: The parsed JSON output from the command if successful,
                     otherwise the raw string output or an error message.
    """
    print(
        f'Tool: Running droidrun_portal_adb_command(portal_path="{portal_path}", action="{action}", data={str(data)})'
    )

    # 1. Input Validation
    if action not in ["query", "insert"]:
        return "Error: Invalid action. Must be 'query' or 'insert'."
    if action == "insert" and not isinstance(data, dict):
        return "Error: The 'insert' action requires a 'data' dictionary."

    # 2. Command Construction
    base_uri = "content://com.droidrun.portal/"
    full_cmd = f"adb shell content {action} --uri {base_uri}{portal_path}"

    if action == "insert" and data:
        bind_args = []
        for key, value in data.items():
            if isinstance(value, str):
                bind_args.append(f"--bind {key}:s:{shlex.quote(value)}")
            elif isinstance(value, int):
                bind_args.append(f"--bind {key}:i:{value}")
            else:
                # Fallback for other types, treat as string
                bind_args.append(f"--bind {key}:s:{shlex.quote(str(value))}")
        full_cmd += " " + " ".join(bind_args)

    # 3. Execution and Output Parsing
    if not user_confirm(f"Run Droidrun-Portal ADB command: {full_cmd}?"):
        return "Denied by user."

    try:
        result_text = run_command(full_cmd, shell=True, check_output=True)
        try:
            # Attempt to parse the output as JSON for structured data
            return json.loads(result_text)
        except json.JSONDecodeError:
            # If parsing fails, return the raw text
            return result_text
    except Exception as e:
        return f"Error executing Droidrun-Portal ADB command: {e}"


tool_definitions = {
    "execute_droidrun_command": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="execute_droidrun_command",
                description="Executes a Droidrun CLI command.",
                parameters={
                    "type": "object",
                    "properties": {"command": {"type": "string"}},
                    "required": ["command"],
                },
            )
        ]
    ),
    "droidrun_portal_adb_command": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="droidrun_portal_adb_command",
                description="Interacts with Droidrun-Portal via ADB commands.",
                parameters={
                    "type": "object",
                    "properties": {
                        "portal_path": {"type": "string"},
                        "action": {"type": "string"},
                        "data": {"type": "object"},
                    },
                    "required": ["portal_path"],
                },
            )
        ]
    ),
}
