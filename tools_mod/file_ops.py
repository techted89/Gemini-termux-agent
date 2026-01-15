import os
import sys
import shutil
import shlex
import fnmatch
import re
import google.genai as genai
from utils.commands import run_command
from google.genai import types as genai_types


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
    except Exception as e:
        return f"Error creating directory: {e}"


def list_directory_recursive_task(directory_path):
    try:
        listing = []
        for root, dirs, files in os.walk(os.path.expanduser(directory_path)):
            level = root.replace(os.path.expanduser(directory_path), "").count(os.sep)
            indent = " " * 4 * (level)
            listing.append(f"{indent}{os.path.basename(root)}/")
            subindent = " " * 4 * (level + 1)
            for f in files:
                listing.append(f"{subindent}{f}")
        return "\n".join(listing)
    except Exception as e:
        return f"Error listing directory: {e}"


def copy_file_task(src, dst):
    try:
        shutil.copy2(os.path.expanduser(src), os.path.expanduser(dst))
        return f"Copied {src} to {dst}"
    except Exception as e:
        return f"Error copying: {e}"


def move_file_task(src, dst):
    try:
        shutil.move(os.path.expanduser(src), os.path.expanduser(dst))
        return f"Moved {src} to {dst}"
    except Exception as e:
        return f"Error moving: {e}"


def find_files_task(
    directory_path, name_pattern=None, content_pattern=None, max_depth=-1
):
    print(f"Tool: Running find_files_task...")
    expanded_path = os.path.expanduser(directory_path)
    found_files = []
    try:
        for root, _, files in os.walk(expanded_path):
            for filename in files:
                if name_pattern and not fnmatch.fnmatch(filename, name_pattern):
                    continue
                filepath = os.path.join(root, filename)
                if content_pattern:
                    try:
                        with open(filepath, "r", errors="ignore") as f:
                            if not re.search(content_pattern, f.read()):
                                continue
                    except:
                        continue
                found_files.append(filepath)
        return "\n".join(found_files) if found_files else "No files found."
    except Exception as e:
        return f"Error finding files: {e}"


def compress_path_task(source_path, output_archive_path, format="zip"):
    try:
        base_name = os.path.splitext(os.path.expanduser(output_archive_path))[0]
        shutil.make_archive(
            base_name,
            format,
            root_dir=os.path.dirname(os.path.expanduser(source_path)),
            base_dir=os.path.basename(os.path.expanduser(source_path)),
        )
        return f"Compressed to {output_archive_path}"
    except Exception as e:
        return f"Error compressing: {e}"


def decompress_archive_task(archive_path, destination_path):
    try:
        shutil.unpack_archive(
            os.path.expanduser(archive_path), os.path.expanduser(destination_path)
        )
        return f"Extracted to {destination_path}"
    except Exception as e:
        return f"Error extracting: {e}"


def open_in_external_editor_task(filepath):
    """Opens a file in an external editor, trying xdg-open first and falling back to termux-open."""
    filepath = os.path.expanduser(filepath)
    if shutil.which("xdg-open"):
        try:
            run_command(f"xdg-open {shlex.quote(filepath)}", shell=True)
            return f"Opened {filepath} with xdg-open."
        except Exception as e:
            print(f"xdg-open failed: {e}")

    if shutil.which("termux-open"):
        try:
            run_command(f"termux-open {shlex.quote(filepath)}", shell=True)
            return f"Opened {filepath} with termux-open."
        except Exception as e:
            return f"Error with termux-open: {e}"

    return "Error: Could not find a suitable command to open the file."

def stat_task(path):
    """Gets file or directory status."""
    try:
        return run_command(f"stat {shlex.quote(os.path.expanduser(path))}", shell=True, check_output=True)
    except Exception as e:
        return f"Error: {e}"

def chmod_task(path, mode):
    """Changes file or directory permissions."""
    try:
        return run_command(f"chmod {mode} {shlex.quote(os.path.expanduser(path))}", shell=True, check_output=True)
    except Exception as e:
        return f"Error: {e}"


def tool_definitions():
    return [
        genai_types.Tool(
            function_declarations=[
                genai_types.FunctionDeclaration(
                    name="lint_python_file",
                    description="Lint Python",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={"filepath": genai_types.Schema(type=genai_types.Type.STRING)},
                        required=["filepath"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="format_code",
                    description="Format Python",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={"filepath": genai_types.Schema(type=genai_types.Type.STRING)},
                        required=["filepath"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="apply_sed",
                    description="Apply Sed",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "filepath": genai_types.Schema(type=genai_types.Type.STRING),
                            "sed_expression": genai_types.Schema(type=genai_types.Type.STRING),
                        },
                        required=["filepath", "sed_expression"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="create_directory",
                    description="Create Dir",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={"directory_path": genai_types.Schema(type=genai_types.Type.STRING)},
                        required=["directory_path"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="list_directory_recursive",
                    description="List Dir",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={"directory_path": genai_types.Schema(type=genai_types.Type.STRING)},
                        required=["directory_path"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="copy_file",
                    description="Copy File",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "source_path": genai_types.Schema(type=genai_types.Type.STRING),
                            "destination_path": genai_types.Schema(type=genai_types.Type.STRING),
                        },
                        required=["source_path", "destination_path"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="move_file",
                    description="Move File",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "source_path": genai_types.Schema(type=genai_types.Type.STRING),
                            "destination_path": genai_types.Schema(type=genai_types.Type.STRING),
                        },
                        required=["source_path", "destination_path"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="find_files",
                    description="Find Files",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "directory_path": genai_types.Schema(type=genai_types.Type.STRING),
                            "name_pattern": genai_types.Schema(type=genai_types.Type.STRING),
                            "content_pattern": genai_types.Schema(type=genai_types.Type.STRING),
                            "max_depth": genai_types.Schema(type=genai_types.Type.INTEGER),
                        },
                        required=["directory_path"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="compress_path",
                    description="Compress",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "source_path": genai_types.Schema(type=genai_types.Type.STRING),
                            "output_archive_path": genai_types.Schema(type=genai_types.Type.STRING),
                            "format": genai_types.Schema(type=genai_types.Type.STRING),
                        },
                        required=["source_path", "output_archive_path"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="decompress_archive",
                    description="Decompress",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "archive_path": genai_types.Schema(type=genai_types.Type.STRING),
                            "destination_path": genai_types.Schema(type=genai_types.Type.STRING),
                        },
                        required=["archive_path", "destination_path"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="open_in_external_editor",
                    description="Open Editor",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={"filepath": genai_types.Schema(type=genai_types.Type.STRING)},
                        required=["filepath"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="stat",
                    description="Get file or directory status.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={"path": genai_types.Schema(type=genai_types.Type.STRING)},
                        required=["path"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="chmod",
                    description="Change file or directory permissions.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "path": genai_types.Schema(type=genai_types.Type.STRING),
                            "mode": genai_types.Schema(type=genai_types.Type.STRING),
                        },
                        required=["path", "mode"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="save_to_file",
                    description="Save content to a file.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "filename": genai_types.Schema(type=genai_types.Type.STRING),
                            "content": genai_types.Schema(type=genai_types.Type.STRING),
                        },
                        required=["filename", "content"],
                    ),
                ),
            ]
        )
    ]

library = {
    "lint_python_file": lint_python_file_task,
    "format_code": format_code_task,
    "apply_sed": apply_sed_task,
    "create_directory": create_directory_task,
    "list_directory_recursive": list_directory_recursive_task,
    "copy_file": copy_file_task,
    "move_file": move_file_task,
    "find_files": find_files_task,
    "compress_path": compress_path_task,
    "decompress_archive": decompress_archive_task,
    "open_in_external_editor": open_in_external_editor_task,
    "stat": stat_task,
    "chmod": chmod_task,
}
