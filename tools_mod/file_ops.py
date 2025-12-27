import os
import sys
import shutil
import shlex
import fnmatch
import re
import google.genai as genai
from utils.commands import run_command


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
    try:
        cmd = f"termux-file-editor {shlex.quote(os.path.expanduser(filepath))}"
        run_command(cmd, shell=True)
        return f"Opened {filepath} in external editor."
    except Exception as e:
        return f"Error: {e}"


tool_definitions = {
    "lint_python_file": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="lint_python_file",
                description="Lint Python",
                parameters={
                    "type": "object",
                    "properties": {"filepath": {"type": "string"}},
                    "required": ["filepath"],
                },
            )
        ]
    ),
    "format_code": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="format_code",
                description="Format Python",
                parameters={
                    "type": "object",
                    "properties": {"filepath": {"type": "string"}},
                    "required": ["filepath"],
                },
            )
        ]
    ),
    "apply_sed": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="apply_sed",
                description="Apply Sed",
                parameters={
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string"},
                        "sed_expression": {"type": "string"},
                    },
                    "required": ["filepath", "sed_expression"],
                },
            )
        ]
    ),
    "create_directory": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="create_directory",
                description="Create Dir",
                parameters={
                    "type": "object",
                    "properties": {"directory_path": {"type": "string"}},
                    "required": ["directory_path"],
                },
            )
        ]
    ),
    "list_directory_recursive": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="list_directory_recursive",
                description="List Dir",
                parameters={
                    "type": "object",
                    "properties": {"directory_path": {"type": "string"}},
                    "required": ["directory_path"],
                },
            )
        ]
    ),
    "copy_file": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="copy_file",
                description="Copy File",
                parameters={
                    "type": "object",
                    "properties": {
                        "source_path": {"type": "string"},
                        "destination_path": {"type": "string"},
                    },
                    "required": ["source_path", "destination_path"],
                },
            )
        ]
    ),
    "move_file": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="move_file",
                description="Move File",
                parameters={
                    "type": "object",
                    "properties": {
                        "source_path": {"type": "string"},
                        "destination_path": {"type": "string"},
                    },
                    "required": ["source_path", "destination_path"],
                },
            )
        ]
    ),
    "find_files": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="find_files",
                description="Find Files",
                parameters={
                    "type": "object",
                    "properties": {
                        "directory_path": {"type": "string"},
                        "name_pattern": {"type": "string"},
                        "content_pattern": {"type": "string"},
                        "max_depth": {"type": "integer"},
                    },
                    "required": ["directory_path"],
                },
            )
        ]
    ),
    "compress_path": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="compress_path",
                description="Compress",
                parameters={
                    "type": "object",
                    "properties": {
                        "source_path": {"type": "string"},
                        "output_archive_path": {"type": "string"},
                        "format": {"type": "string"},
                    },
                    "required": ["source_path", "output_archive_path"],
                },
            )
        ]
    ),
    "decompress_archive": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="decompress_archive",
                description="Decompress",
                parameters={
                    "type": "object",
                    "properties": {
                        "archive_path": {"type": "string"},
                        "destination_path": {"type": "string"},
                    },
                    "required": ["archive_path", "destination_path"],
                },
            )
        ]
    ),
    "open_in_external_editor": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="open_in_external_editor",
                description="Open Editor",
                parameters={
                    "type": "object",
                    "properties": {"filepath": {"type": "string"}},
                    "required": ["filepath"],
                },
            )
        ]
    ),
}
