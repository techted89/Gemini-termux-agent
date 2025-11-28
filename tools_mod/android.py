import os
import shlex
import json
import tempfile
import re
import xml.etree.ElementTree as ET
import google.generativeai as genai
from helpers import run_command, user_confirm

# Assume uiautomator2 is a Python library available in the Termux environment
try:
    import uiautomator2 as u2
except ImportError:
    u2 = None
    print("Warning: uiautomator2 library not found. UI automation tools will not be available.")

def open_gemini_app_task(package_name="com.google.android.apps.bard"):
    """
    Opens the Gemini app using uiautomator2.
    Assumes uiautomator2 is installed and configured to interact with Android UI.
    """
    if u2 is None:
        return "Error: uiautomator2 library is not available. Please install it with `pip install uiautomator2` and ensure `atx-agent` is running on your device."
    try:
        d = u2.connect() # Connect to device
        d.app_start(package_name, stop=True) # Stop and start the app to ensure a fresh launch
        return f"Successfully opened the app with package name: {package_name}"
    except Exception as e:
        return f"Error opening Gemini app with uiautomator2: {e}"

def android_ui_find_and_tap_text(text, timeout=10):
    """
    Finds a UI element by text and taps it.
    """
    if u2 is None:
        return "Error: uiautomator2 library is not available. Please install it with `pip install uiautomator2` and ensure `atx-agent` is running on your device."
    try:
        d = u2.connect()
        if d(text=text).wait(timeout=timeout*1000):
            d(text=text).click()
            return f"Successfully tapped element with text: {text}"
        else:
            return f"Error: Element with text '{text}' not found within {timeout} seconds."
    except Exception as e:
        return f"Error finding and tapping element by text: {e}"

def android_ui_long_press_text(text, duration=1.0, timeout=10):
    """
    Finds a UI element by text and performs a long press on it.
    """
    if u2 is None:
        return "Error: uiautomator2 library is not available. Please install it with `pip install uiautomator2` and ensure `atx-agent` is running on your device."
    try:
        d = u2.connect()
        if d(text=text).wait(timeout=timeout*1000):
            d(text=text).long_click(duration=duration)
            return f"Successfully long-pressed element with text: {text} for {duration} seconds"
        else:
            return f"Error: Element with text '{text}' not found within {timeout} seconds."
    except Exception as e:
        return f"Error long-pressing element by text: {e}"

def tap_screen(x, y):
    """
    Simulates a screen tap at the specified coordinates using root privileges.

    Args:
        x (int): The x-coordinate of the tap location.
        y (int): The y-coordinate of the tap location.

    Returns:
        str: The result of the command execution or an error message.
    """
    print(f"Tool: Running tap_screen(x={x}, y={y})")
    cmd = f'su -c "input tap {x} {y}"'
    if user_confirm(f"Execute root command: {cmd}?"):
        try:
            return run_command(cmd, shell=True, check_output=True) or f"Tapped screen at ({x}, {y})."
        except Exception as e:
            return f"Error tapping screen: {e}"
    return "Denied by user."

def swipe_screen(x1, y1, x2, y2, duration_ms=300):
    """
    Simulates a swipe gesture on the screen using root privileges.

    Args:
        x1 (int): The starting x-coordinate of the swipe.
        y1 (int): The starting y-coordinate of the swipe.
        x2 (int): The ending x-coordinate of the swipe.
        y2 (int): The ending y-coordinate of the swipe.
        duration_ms (int, optional): The duration of the swipe in milliseconds. Defaults to 300.

    Returns:
        str: The result of the command execution or an error message.
    """
    print(f"Tool: Running swipe_screen(from=({x1}, {y1}), to=({x2}, {y2}), duration={duration_ms}ms)")
    cmd = f'su -c "input swipe {x1} {y1} {x2} {y2} {duration_ms}"'
    if user_confirm(f"Execute root command: {cmd}?"):
        try:
            return run_command(cmd, shell=True, check_output=True) or f"Swiped screen from ({x1}, {y1}) to ({x2}, {y2})."
        except Exception as e:
            return f"Error swiping screen: {e}"
    return "Denied by user."

def input_text(text):
    """
    Inputs the given text into the current input field using root privileges.

    Args:
        text (str): The text to be inputted.

    Returns:
        str: The result of the command execution or an error message.
    """
    print(f"Tool: Running input_text(text=\"{text}\")")
    # Note: shlex.quote is crucial here to handle spaces and special characters safely.
    cmd = f'su -c "input text {shlex.quote(text)}"'
    if user_confirm(f"Execute root command: {cmd}?"):
        try:
            return run_command(cmd, shell=True, check_output=True) or f"Inputted text: '{text}'."
        except Exception as e:
            return f"Error inputting text: {e}"
    return "Denied by user."

def get_screen_analysis(output_path="/sdcard/Pictures/screen_analysis.png"):
    """
    Captures the screen and UI XML hierarchy for analysis.

    This tool provides a comprehensive snapshot of the current UI state by:
    1.  Taking a screenshot of the device.
    2.  Dumping the UI's XML layout.

    Args:
        output_path (str, optional): The path to save the screenshot and XML dump.
            The XML file will have the same name with a '.xml' extension.
            Defaults to "/sdcard/Pictures/screen_analysis.png".

    Returns:
        str: A message containing the path to the screenshot and the UI XML content,
             or an error message if the commands fail.
    """
    print(f"Tool: Running get_screen_analysis(output_path=\"{output_path}\")")
    xml_output_path = os.path.splitext(output_path)[0] + ".xml"

    # Define the root commands
    screencap_cmd = f'su -c "screencap -p {shlex.quote(output_path)}"'
    uiautomator_cmd = f'su -c "uiautomator dump {shlex.quote(xml_output_path)}"'

    if not user_confirm("Proceed with screen capture and UI dump?"):
        return "Denied by user."

    try:
        # Execute screen capture
        run_command(screencap_cmd, shell=True, check_output=True)
        # Execute UI dump
        run_command(uiautomator_cmd, shell=True, check_output=True)

        # Read the XML content
        with open(xml_output_path, "r") as f:
            xml_content = f.read()

        return f"Screen captured at '{output_path}'.\nUI XML content:\n{xml_content}"

    except Exception as e:
        return f"Error during screen analysis: {e}"

def extract_text_from_screen():
    """
    Extracts all text from the current screen by parsing the UI XML hierarchy.

    This tool is useful for reading the content of the screen without needing OCR.
    It calls `get_screen_analysis` to get the UI dump and then extracts the 'text'
    attribute from each node in the XML tree.

    Returns:
        list[str]: A list of all non-empty text strings found on the screen.
    """
    print("Tool: Running extract_text_from_screen()")

    # Use a temporary file for the analysis to avoid overwriting user files
    temp_dir = tempfile.gettempdir()
    analysis_path = os.path.join(temp_dir, "screen_analysis.png")

    # Get the screen analysis (screenshot and XML)
    analysis_result = get_screen_analysis(output_path=analysis_path)

    if "Error" in analysis_result:
        return f"Error getting screen analysis: {analysis_result}"

    xml_output_path = os.path.splitext(analysis_path)[0] + ".xml"

    try:
        # Parse the XML file
        tree = ET.parse(xml_output_path)
        root = tree.getroot()

        texts = []
        for node in root.iter():
            text = node.get("text")
            if text and text.strip():
                texts.append(text.strip())

        return texts if texts else "No text found on the screen."

    except ET.ParseError as e:
        return f"Error parsing UI XML: {e}"
    except Exception as e:
        return f"An unexpected error occurred during text extraction: {e}"
    finally:
        # Clean up the temporary files
        if os.path.exists(analysis_path):
            os.remove(analysis_path)
        if os.path.exists(xml_output_path):
            os.remove(xml_output_path)

def execute_droidrun_command(command):
    """Executes a Droidrun CLI command."""
    print(f"Tool: Running execute_droidrun_command(command=\"{command}\")")
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
    print(f'Tool: Running droidrun_portal_adb_command(portal_path="{portal_path}", action="{action}", data={str(data)})')

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

def connect_uiautomator2(addr=None):
    """Establishes connection to the Android device."""
    if u2 is None:
        return "Error: uiautomator2 not available."
    try:
        d = u2.connect(addr)
        info = d.info
        return f"Connected: {info}"
    except Exception as e:
        return f"Error connecting: {e}"

def android_ui_tap(x=None, y=None, selector=None):
    """Simulates a screen tap by coordinates or UI element selector."""
    if u2 is None: return "Error: uiautomator2 not available."
    try:
        d = u2.connect()
        if x is not None and y is not None:
            d.click(x, y)
            return f"Tapped at ({x}, {y})"
        if selector:
            d(text=selector).click() # Simplified selector assumption
            return f"Tapped element: {selector}"
        return "Error: Need coordinates or selector."
    except Exception as e:
        return f"Error tapping: {e}"

def android_ui_set_text(selector, text):
    """Inputs text into a UI field by selector."""
    if u2 is None: return "Error: uiautomator2 not available."
    try:
        d = u2.connect()
        d(text=selector).set_text(text)
        return f"Set text '{text}' on '{selector}'"
    except Exception as e:
        return f"Error setting text: {e}"

def android_ui_dump_hierarchy():
    """Reads the current screen's XML hierarchy."""
    return get_screen_analysis()

definitions = {
    "connect_uiautomator2": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="connect_uiautomator2", description="Connect to uiautomator2.", parameters={"type": "object", "properties": {"addr": {"type": "string"}}, "required": []})]),
    "android_ui_tap": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="android_ui_tap", description="Tap screen by coords or selector.", parameters={"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}, "selector": {"type": "string"}}, "required": []})]),
    "android_ui_set_text": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="android_ui_set_text", description="Set text on UI element.", parameters={"type": "object", "properties": {"selector": {"type": "string"}, "text": {"type": "string"}}, "required": ["selector", "text"]})]),
    "android_ui_dump_hierarchy": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="android_ui_dump_hierarchy", description="Dump UI hierarchy.", parameters={"type": "object", "properties": {}})]),
    "open_gemini_app": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="open_gemini_app", description="Opens the Gemini app using uiautomator2. Requires uiautomator2 library and atx-agent to be installed and running.", parameters={"type": "object", "properties": {"package_name": {"type": "string"}}, "required": []})]),
    "android_ui_find_and_tap_text": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="android_ui_find_and_tap_text", description="Finds a UI element by text and taps it.", parameters={"type": "object", "properties": {"text": {"type": "string"}, "timeout": {"type": "number", "format": "float"}}, "required": ["text"]})]),
    "android_ui_long_press_text": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="android_ui_long_press_text", description="Finds a UI element by text and performs a long press on it.", parameters={"type": "object", "properties": {"text": {"type": "string"}, "duration": {"type": "number", "format": "float"}, "timeout": {"type": "number", "format": "float"}}, "required": ["text"]})]),
    "tap_screen": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="tap_screen", description="Taps the screen at given coordinates.", parameters={"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]})]),
    "swipe_screen": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="swipe_screen", description="Swipes on the screen.", parameters={"type": "object", "properties": {"x1": {"type": "integer"}, "y1": {"type": "integer"}, "x2": {"type": "integer"}, "y2": {"type": "integer"}, "duration_ms": {"type": "integer"}}, "required": ["x1", "y1", "x2", "y2"]})]),
    "input_text": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="input_text", description="Inputs text.", parameters={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]})]),
    "get_screen_analysis": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="get_screen_analysis", description="Captures screen and UI XML.", parameters={"type": "object", "properties": {"output_path": {"type": "string"}}, "required": []})]),
    "extract_text_from_screen": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="extract_text_from_screen", description="Extracts all text from the screen.", parameters={"type": "object", "properties": {}})]),
    "execute_droidrun_command": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="execute_droidrun_command", description="Executes a Droidrun CLI command.", parameters={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]})]),
    "droidrun_portal_adb_command": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="droidrun_portal_adb_command", description="Interacts with Droidrun-Portal via ADB commands.", parameters={"type": "object", "properties": {"portal_path": {"type": "string"}, "action": {"type": "string"}, "data": {"type": "object"}}, "required": ["portal_path"]})]),
}
