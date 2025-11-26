
import google.generativeai as genai
import tempfile
import os
import sys
import shutil
import requests
from bs4 import BeautifulSoup
import shlex
import fnmatch
import re
import json

import xml.etree.ElementTree as ET
main
from googleapiclient.discovery import build
import config
from config import VPS_USER, VPS_IP, VPS_SSH_KEY_PATH
from db import learn_directory, learn_url, learn_file_content, search_and_delete_knowledge, search_and_delete_history
from helpers import run_command, user_confirm, save_to_file

# Assume uiautomator2 is a Python library available in the Termux environment
try:
    import uiautomator2 as u2
except ImportError:
    u2 = None
    print("Warning: uiautomator2 library not found. UI automation tools will not be available.")

# --- Core Tools ---

def google_search(query):
    """A tool that can search the web."""
    print(f"Tool: Running google_search(query=\"{query}\")")
    if not config.GOOGLE_API_KEY or config.GOOGLE_API_KEY == "YOUR_GOOGLE_SEARCH_API_KEY":
        return "Error: GOOGLE_API_KEY is not set in config.py."
    try:
        service = build("customsearch", "v1", developerKey=config.GOOGLE_API_KEY)
        res = service.cse().list(q=query, cx=config.CUSTOM_SEARCH_CX, num=3).execute()
        snippets = [f"Title: {item['title']}\nSnippet: {item['snippet']}\nSource: {item['link']}"
                    for item in res.get('items', [])]
        if not snippets: return "No search results found."
        return "\n---\n".join(snippets)
    except Exception as e:
        return f"Error during search: {e}"

def learn_repo_task(repo_url):
    """Wrapper for learn_repo to be called by the agent."""
    print(f"Tool: Running learn_repo_task(repo_url=\"{repo_url}\")")
    if not (repo_url.startswith("http") and repo_url.endswith(".git")):
        return "Error: Agent passed an invalid .git URL"
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"Cloning {repo_url} into {temp_dir}...")
            run_command(f"git clone --depth 1 {repo_url} {temp_dir}", shell=True)
            print("Clone complete. Learning from directory...")
            learn_directory(temp_dir)
            return "Learning complete. Temporary directory auto-cleaned."
    except Exception as e:
        return f"Error during repo learning: {e}"

def read_file_task(filepath):
    """Wrapper for reading a file to be called by the agent."""
    print(f"Tool: Running read_file_task(filepath=\"{filepath}\")")
    try:
        filepath = os.path.expanduser(filepath)
        with open(filepath, 'r') as f:
            content = f.read()
        return f"CONTEXT FILE ({filepath}):\n---\n{content}\n---"
    except Exception as e:
        return f"Error reading file {filepath}: {e}"

def execute_shell_command(cmd):
    """Executes a shell command on the local system after user confirmation."""
    if user_confirm(f"Run: {cmd}?"):
        return run_command(cmd, shell=True, check_output=True)
    return "Denied."

def create_file_task(filepath, content=""):
    """Creates a new file at the specified path with optional content."""
    print(f"Tool: Running create_file_task(filepath='{filepath}')")
    try:
        expanded_filepath = os.path.expanduser(filepath)
        parent_dir = os.path.dirname(expanded_filepath)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)
        with open(expanded_filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Created file: {filepath}"
    except Exception as e:
        return f"Error creating file {filepath}: {e}"

# --- Helper Tools (Linting/Formatting/File Ops) ---

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

def apply_sed_task(filepath, sed_expression, in_place=True):
    """Applies a SED command."""
    expanded_filepath = os.path.expanduser(filepath)
    full_cmd = f"sed {'-i' if in_place else ''} {shlex.quote(sed_expression)} {shlex.quote(expanded_filepath)}"
    try:
        result = run_command(full_cmd, shell=True, check_output=True)
        return result or "Sed applied."
    except Exception as e:
        return f"Sed Error: {e}"

def create_directory_task(directory_path):
    try:
        os.makedirs(os.path.expanduser(directory_path), exist_ok=True)
        return f"Created directory: {directory_path}"
    except Exception as e: return f"Error creating directory: {e}"

def list_directory_recursive_task(directory_path):
    try:
        listing = []
        for root, dirs, files in os.walk(os.path.expanduser(directory_path)):
            level = root.replace(os.path.expanduser(directory_path), '').count(os.sep)
            indent = ' ' * 4 * (level)
            listing.append(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 4 * (level + 1)
            for f in files:
                listing.append(f"{subindent}{f}")
        return "\n".join(listing)
    except Exception as e: return f"Error listing directory: {e}"

def copy_file_task(src, dst):
    try:
        shutil.copy2(os.path.expanduser(src), os.path.expanduser(dst))
        return f"Copied {src} to {dst}"
    except Exception as e: return f"Error copying: {e}"

def move_file_task(src, dst):
    try:
        shutil.move(os.path.expanduser(src), os.path.expanduser(dst))
        return f"Moved {src} to {dst}"
    except Exception as e: return f"Error moving: {e}"

def find_files_task(directory_path, name_pattern=None, content_pattern=None, max_depth=-1):
    print(f'Tool: Running find_files_task...')
    expanded_path = os.path.expanduser(directory_path)
    found_files = []
    try:
        for root, _, files in os.walk(expanded_path):
            for filename in files:
                if name_pattern and not fnmatch.fnmatch(filename, name_pattern): continue
                filepath = os.path.join(root, filename)
                if content_pattern:
                    try:
                        with open(filepath, 'r', errors='ignore') as f:
                            if not re.search(content_pattern, f.read()): continue
                    except: continue
                found_files.append(filepath)
        return "\n".join(found_files) if found_files else "No files found."
    except Exception as e: return f"Error finding files: {e}"

def compress_path_task(source_path, output_archive_path, format="zip"):
    try:
        base_name = os.path.splitext(os.path.expanduser(output_archive_path))[0]
        shutil.make_archive(base_name, format, root_dir=os.path.dirname(os.path.expanduser(source_path)), base_dir=os.path.basename(os.path.expanduser(source_path)))
        return f"Compressed to {output_archive_path}"
    except Exception as e: return f"Error compressing: {e}"

def decompress_archive_task(archive_path, destination_path):
    try:
        shutil.unpack_archive(os.path.expanduser(archive_path), os.path.expanduser(destination_path))
        return f"Extracted to {destination_path}"
    except Exception as e: return f"Error extracting: {e}"

def open_in_external_editor_task(filepath):
    try:
        cmd = f"termux-file-editor {shlex.quote(os.path.expanduser(filepath))}"
        run_command(cmd, shell=True)
        return f"Opened {filepath} in external editor."
    except Exception as e: return f"Error: {e}"

# --- UI Automation Tools ---
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

# --- Root-Based UI Automation Tools ---

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

# --- Browser Automation Tools (Puppeteer) ---
def execute_puppeteer_script(url, action="screenshot", output_file="screenshot.png"):
    """
    Executes a Puppeteer script to automate a Chromium browser on Termux.
    Currently supports 'screenshot' and 'get_html' actions.
    """
    print(f"Tool: Running execute_puppeteer_script(url=\"{url}\", action=\"{action}\")")
    if user_confirm(f"Execute Puppeteer script for URL: {url} with action: {action}?"):
        script_content = f'''
const puppeteer = require('puppeteer');

(async () => {{
    const browser = await puppeteer.launch({{
        executablePath: '/data/data/com.termux/files/usr/bin/chromium',
        args: ['--no-sandbox']
    }});
    const page = await browser.newPage();
    await page.goto('{url}', {{waitUntil: 'networkidle2'}});

    if ("{action}" === "screenshot") {{
        await page.screenshot({{path: '{output_file}'}});
        console.log(`Screenshot saved to {output_file}`);
    }} else if ("{action}" === "get_html") {{
        const html = await page.content();
        console.log(html);
    }} else {{
        console.log(`Unknown action: {action}`);
    }}

    await browser.close();
}})();
'''
        # Create a temporary JavaScript file
        temp_js_path = os.path.join(tempfile.gettempdir(), "puppeteer_script.js")
        with open(temp_js_path, "w") as f:
            f.write(script_content)

        try:
            result = run_command(f"node {shlex.quote(temp_js_path)}", shell=True, check_output=True)
            return result
        except Exception as e:
            return f"Error executing Puppeteer script: {e}"
        finally:
            if os.path.exists(temp_js_path):
                os.remove(temp_js_path)
    return "Denied."

# --- Droidrun Tools ---
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

# --- CM Tools ---
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

# --- Git Tools ---
def git_status_task():
    return run_command("git status --short", shell=True, check_output=True) or "Working tree clean."

def git_pull_task(branch="main"):
    return run_command(f"git pull origin {branch}", shell=True, check_output=True)

def git_push_task(branch="main"):
    return run_command(f"git push origin {branch}", shell=True, check_output=True)

def git_branch_task(new_branch_name=None):
    if new_branch_name:
        return run_command(f"git checkout -b {new_branch_name}", shell=True, check_output=True)
    return run_command("git branch", shell=True, check_output=True)

# --- Tool Dispatcher ---
def execute_tool(call, models):
    import tasks # Lazy import
    from api import agentic_plan, agentic_reason, agentic_execute

    n = call.name; a = call.args
    try:
        # Basic Tools
        if n == "google_search": return google_search(a["query"])
        if n == "learn_from_url_or_repo": return learn_repo_task(a["url"]) if a["url"].endswith(".git") else learn_url(a["url"])
        if n == "read_file": return read_file_task(a["filepath"])
        if n == "execute_shell_command":
            # Handle vps_target logic
            if a.get("vps_target"):
                 if not VPS_USER or not VPS_IP or not VPS_SSH_KEY_PATH: return "Error: VPS config missing."
                 ssh_cmd = a.get("ssh_command")
                 full_cmd = f'ssh -i {VPS_SSH_KEY_PATH} {VPS_USER}@{VPS_IP} "{ssh_cmd}"'
                 print(f"🤖 Running on VPS: {full_cmd}")
                 if user_confirm("Approve VPS command?"): return run_command(full_cmd, shell=True, check_output=True)
                 return "Denied."
            return execute_shell_command(a["command"])
        if n == "create_file": return create_file_task(a["filepath"], a.get("content", ""))

        # Helper Tools
        if n == "lint_python_file": return lint_python_file_task(a["filepath"], a.get("linter", "flake8"))
        if n == "format_code": return format_code_task(a["filepath"], a.get("formatter", "black"))
        if n == "apply_sed": return apply_sed_task(a["filepath"], a["sed_expression"], a.get("in_place", True))
        if n == "create_directory": return create_directory_task(a["directory_path"])
        if n == "list_directory_recursive": return list_directory_recursive_task(a["directory_path"])
        if n == "copy_file": return copy_file_task(a["source_path"], a["destination_path"])
        if n == "move_file": return move_file_task(a["source_path"], a["destination_path"])
        if n == "find_files": return find_files_task(a["directory_path"], a.get("name_pattern"), a.get("content_pattern"), a.get("max_depth", -1))
        if n == "compress_path": return compress_path_task(a["source_path"], a["output_archive_path"], a.get("format", "zip"))
        if n == "decompress_archive": return decompress_archive_task(a["archive_path"], a["destination_path"])
        if n == "open_in_external_editor": return open_in_external_editor_task(a["filepath"])

        # UI Automation Tools
        if n == "open_gemini_app": return open_gemini_app_task(a.get("package_name", "com.google.android.apps.bard"))
        if n == "android_ui_find_and_tap_text": return android_ui_find_and_tap_text(a["text"], a.get("timeout", 10))
        if n == "android_ui_long_press_text": return android_ui_long_press_text(a["text"], a.get("duration", 1.0), a.get("timeout", 10))

        # Root-Based UI Automation Tools
        if n == "tap_screen": return tap_screen(a["x"], a["y"])
        if n == "swipe_screen": return swipe_screen(a["x1"], a["y1"], a["x2"], a["y2"], a.get("duration_ms", 300))
        if n == "input_text": return input_text(a["text"])
        if n == "get_screen_analysis": return get_screen_analysis(a.get("output_path", "/sdcard/Pictures/screen_analysis.png"))
        if n == "extract_text_from_screen": return extract_text_from_screen()

        # Browser Automation Tools (Puppeteer)
        if n == "execute_puppeteer_script": return execute_puppeteer_script(a["url"], a.get("action", "screenshot"), a.get("output_file", "screenshot.png"))

        # Droidrun Tools
        if n == "execute_droidrun_command": return execute_droidrun_command(a["command"])
        if n == "droidrun_portal_adb_command": return droidrun_portal_adb_command(a["portal_path"], a.get("action", "query"), a.get("data"))

        # CM Tools
        if n == "execute_cm_command": return execute_cm_command(a["cm_command"])

        # Git Tools
        if n == "git_status": return git_status_task()
        if n == "git_pull": return git_pull_task(a.get("branch", "main"))
        if n == "git_push": return git_push_task(a.get("branch", "main"))
        if n == "git_branch": return git_branch_task(a.get("new_branch_name"))

        # Task Tools
        if n == "edit_file": return tasks.handle_edit_file(models['default'], a["filepath"], a["prompt"], a.get("save_as"))
        if n == "create_project": return tasks.handle_create_project(models['default'], a["prompt"])
        if n == "git_commit": return tasks.handle_git_commit(models['default'], a["prompt"])
        if n == "gh_issue": return tasks.handle_gh_issue(models['default'], a.get("repo"), a["prompt"])
        if n == "generate_image": return tasks.handle_image_generation(models['default'], a["prompt"])
        if n == "install": return tasks.handle_install(models['default'], a["prompt"])

        # DB Tools
        if n == "learn_file_content": return learn_file_content(a["filepath"], a.get("content"))
        if n == "learn_directory": return learn_directory(a["directory_path"], a.get("ignore_patterns"))
        if n == "learn_url": return learn_url(a["url"])
        if n == "search_and_delete_knowledge": return search_and_delete_knowledge(a.get("query"), a.get("source"), a.get("ids"), a.get("confirm"))
        if n == "search_and_delete_history": return search_and_delete_history(a.get("query"), a.get("role"), a.get("ids"), a.get("confirm"))

        # Agentic Meta-Tools
        if n == "agentic_plan": return agentic_plan(a["prompt"], tools=list(tool_definitions.values()))
        if n == "agentic_reason": return agentic_reason(a["prompt"], models['default'])
        if n == "agentic_execute": return agentic_execute(a["prompt"], models['default'])

        return f"Unknown: {n}"
    except Exception as e: return f"Tool Error: {e}"

# --- Definitions ---
tool_definitions = {
    "google_search": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="google_search", description="Search web", parameters={"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]})]),
    "execute_shell_command": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="execute_shell_command", description="Run shell cmd", parameters={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]})]),
    "read_file": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="read_file", description="Read file", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
    "create_file": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="create_file", description="Create File", parameters={"type": "object", "properties": {"filepath": {"type": "string"}, "content": {"type": "string"}}, "required": ["filepath"]})]),
    "learn_from_url_or_repo": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="learn_from_url_or_repo", description="Learn", parameters={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]})]),
    "edit_file": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="edit_file", description="Edit file", parameters={"type": "object", "properties": {"filepath": {"type": "string"}, "prompt": {"type": "string"}, "save_as": {"type": "string"}}, "required": ["filepath", "prompt"]})]),
    "create_project": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="create_project", description="Create project", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
    "git_commit": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="git_commit", description="Git commit", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
    "install": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="install", description="Install Package", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),

    "agentic_plan": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="agentic_plan", description="Create Plan", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
    "agentic_reason": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="agentic_reason", description="Reasoning", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),
    "agentic_execute": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="agentic_execute", description="Execute Action", parameters={"type": "object", "properties": {"prompt": {"type": "string"}}, "required": ["prompt"]})]),

    "lint_python_file": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="lint_python_file", description="Lint Python", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
    "format_code": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="format_code", description="Format Python", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
    "apply_sed": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="apply_sed", description="Apply Sed", parameters={"type": "object", "properties": {"filepath": {"type": "string"}, "sed_expression": {"type": "string"}}, "required": ["filepath", "sed_expression"]})]),
    "create_directory": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="create_directory", description="Create Dir", parameters={"type": "object", "properties": {"directory_path": {"type": "string"}}, "required": ["directory_path"]})]),
    "list_directory_recursive": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="list_directory_recursive", description="List Dir", parameters={"type": "object", "properties": {"directory_path": {"type": "string"}}, "required": ["directory_path"]})]),
    "copy_file": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="copy_file", description="Copy File", parameters={"type": "object", "properties": {"source_path": {"type": "string"}, "destination_path": {"type": "string"}}, "required": ["source_path", "destination_path"]})]),
    "move_file": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="move_file", description="Move File", parameters={"type": "object", "properties": {"source_path": {"type": "string"}, "destination_path": {"type": "string"}}, "required": ["source_path", "destination_path"]})]),
    "find_files": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="find_files", description="Find Files", parameters={"type": "object", "properties": {"directory_path": {"type": "string"}, "name_pattern": {"type": "string"}, "content_pattern": {"type": "string"}, "max_depth": {"type": "integer"}}, "required": ["directory_path"]})]),
    "compress_path": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="compress_path", description="Compress", parameters={"type": "object", "properties": {"source_path": {"type": "string"}, "output_archive_path": {"type": "string"}, "format": {"type": "string"}}, "required": ["source_path", "output_archive_path"]})]),
    "decompress_archive": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="decompress_archive", description="Decompress", parameters={"type": "object", "properties": {"archive_path": {"type": "string"}, "destination_path": {"type": "string"}}, "required": ["archive_path", "destination_path"]})]),
    "open_in_external_editor": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="open_in_external_editor", description="Open Editor", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),

    "open_gemini_app": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="open_gemini_app", description="Opens the Gemini app using uiautomator2. Requires uiautomator2 library and atx-agent to be installed and running.", parameters={"type": "object", "properties": {"package_name": {"type": "string"}}, "required": []})]),
    "android_ui_find_and_tap_text": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="android_ui_find_and_tap_text", description="Finds a UI element by text and taps it.", parameters={"type": "object", "properties": {"text": {"type": "string"}, "timeout": {"type": "number", "format": "float"}}, "required": ["text"]})]),
    "android_ui_long_press_text": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="android_ui_long_press_text", description="Finds a UI element by text and performs a long press on it.", parameters={"type": "object", "properties": {"text": {"type": "string"}, "duration": {"type": "number", "format": "float"}, "timeout": {"type": "number", "format": "float"}}, "required": ["text"]})]),

    "tap_screen": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="tap_screen", description="Taps the screen at given coordinates.", parameters={"type": "object", "properties": {"x": {"type": "integer"}, "y": {"type": "integer"}}, "required": ["x", "y"]})]),
    "swipe_screen": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="swipe_screen", description="Swipes on the screen.", parameters={"type": "object", "properties": {"x1": {"type": "integer"}, "y1": {"type": "integer"}, "x2": {"type": "integer"}, "y2": {"type": "integer"}, "duration_ms": {"type": "integer"}}, "required": ["x1", "y1", "x2", "y2"]})]),
    "input_text": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="input_text", description="Inputs text.", parameters={"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]})]),
    "get_screen_analysis": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="get_screen_analysis", description="Captures screen and UI XML.", parameters={"type": "object", "properties": {"output_path": {"type": "string"}}, "required": []})]),
    "extract_text_from_screen": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="extract_text_from_screen", description="Extracts all text from the screen.", parameters={"type": "object", "properties": {}})]),

    "execute_puppeteer_script": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="execute_puppeteer_script", description="Executes a Puppeteer script for browser automation (screenshot, get_html).", parameters={"type": "object", "properties": {"url": {"type": "string"}, "action": {"type": "string"}, "output_file": {"type": "string"}}, "required": ["url"]})]),

    "execute_droidrun_command": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="execute_droidrun_command", description="Executes a Droidrun CLI command.", parameters={"type": "object", "properties": {"command": {"type": "string"}}, "required": ["command"]})]),
    "droidrun_portal_adb_command": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="droidrun_portal_adb_command", description="Interacts with Droidrun-Portal via ADB commands.", parameters={"type": "object", "properties": {"portal_path": {"type": "string"}, "action": {"type": "string"}, "data": {"type": "object"}}, "required": ["portal_path"]})]),

    "execute_cm_command": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="execute_cm_command", description="Executes a Collective Mind (CM) command.", parameters={"type": "object", "properties": {"cm_command": {"type": "string"}}, "required": ["cm_command"]})]),

    "git_status": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="git_status", description="Git Status", parameters={"type": "object", "properties": {}})]),
    "git_pull": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="git_pull", description="Git Pull", parameters={"type": "object", "properties": {"branch": {"type": "string"}}, "required": []})]),
    "git_push": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="git_push", description="Git Push", parameters={"type": "object", "properties": {"branch": {"type": "string"}}, "required": []})]),
    "git_branch": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="git_branch", description="Git Branch", parameters={"type": "object", "properties": {"new_branch_name": {"type": "string"}}, "required": []})]),

    "learn_file_content": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="learn_file_content", description="Learn File", parameters={"type": "object", "properties": {"filepath": {"type": "string"}}, "required": ["filepath"]})]),
    "learn_directory": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="learn_directory", description="Learn Dir", parameters={"type": "object", "properties": {"directory_path": {"type": "string"}, "ignore_patterns": {"type": "array", "items": {"type": "string"}}}, "required": ["directory_path"]})]),
    "learn_url": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="learn_url", description="Learn URL", parameters={"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]})]),
    "search_and_delete_knowledge": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="search_and_delete_knowledge", description="Search/Del Knowledge", parameters={"type": "object", "properties": {"query": {"type": "string"}, "source": {"type": "string"}, "ids": {"type": "array", "items": {"type": "string"}}, "confirm": {"type": "boolean"}}, "required": []})]),
    "search_and_delete_history": genai.types.Tool(function_declarations=[genai.types.FunctionDeclaration(name="search_and_delete_history", description="Search/Del History", parameters={"type": "object", "properties": {"query": {"type": "string"}, "role": {"type": "string"}, "ids": {"type": "array", "items": {"type": "string"}}, "confirm": {"type": "boolean"}}, "required": []})])
}
