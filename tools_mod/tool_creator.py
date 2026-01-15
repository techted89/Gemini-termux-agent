import os
import re
import google.genai as genai

def create_new_tool_task(module_name, code_content):
    """
    Creates a new Python module in tools_mod/ with the provided content.
    The content should follow the standard pattern:
    - Imports
    - Tool functions
    - tool_definitions() returning List[genai.types.Tool]
    - library dict mapping names to functions
    """
    if not re.match(r"^[a-zA-Z0-9_]+$", module_name):
        return "Error: Invalid module name. Use alphanumeric characters and underscores only."

    filepath = os.path.join("tools_mod", f"{module_name}.py")

    if os.path.exists(filepath):
        return f"Error: Module {module_name} already exists."

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_content)
        return f"Successfully created {filepath}. Now use register_tool_module('{module_name}') to enable it."
    except Exception as e:
        return f"Error creating tool module: {e}"

def register_tool_module_task(module_name):
    """
    Registers a new tool module in tools_mod/__init__.py so it can be used.
    It adds the import, extends tool_definitions, and adds the library lookup.
    """
    if not re.match(r"^[a-zA-Z0-9_]+$", module_name):
        return "Error: Invalid module name."

    init_path = os.path.join("tools_mod", "__init__.py")

    try:
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Add Import
        # Find the line starting with "from . import"
        # We assume there is one main import line.
        # "from . import core, web, file_ops, ..."

        # Check if already imported
        if f", {module_name}" in content or f" {module_name}," in content or f"import {module_name}" in content:
            return f"Module {module_name} seems to be already registered (import found)."

        import_pattern = r"(from \. import [^\n]+)"
        match = re.search(import_pattern, content)
        if match:
            current_imports = match.group(1)
            new_imports = f"{current_imports}, {module_name}"
            content = content.replace(current_imports, new_imports)
        else:
            return "Error: Could not find import line in __init__.py"

        # 2. Add to get_all_tool_definitions
        # Look for "all_tools.extend(learning.tool_definitions())" or similar and append after it.
        # We can append after the last all_tools.extend call.

        # We'll use a specific anchor if possible, or just find the last occurrence.
        # Let's verify the file content structure via read_file first? No, I assume standard structure.
        # I'll look for "    return all_tools" and insert before it.

        def_pattern = r"(    return all_tools)"
        def_insert = f"    all_tools.extend({module_name}.tool_definitions())\n"

        if def_insert not in content:
            content = re.sub(def_pattern, f"{def_insert}\\1", content)

        # 3. Add to execute_tool
        # Look for the last "if hasattr(..., 'library')..." block and append after it.
        # Or just find "# 2. Legacy" and insert before it.

        exec_pattern = r"(    # 2. Legacy / Special Cases)"
        exec_insert = f"""    if hasattr({module_name}, 'library') and name in {module_name}.library:
        return {module_name}.library[name](**args)

"""
        if exec_insert.strip() not in content:
             content = re.sub(exec_pattern, f"{exec_insert}\\1", content)

        with open(init_path, "w", encoding="utf-8") as f:
            f.write(content)

        return f"Successfully registered {module_name}. The new tools should be available."

    except Exception as e:
        return f"Error registering module: {e}"

def tool_definitions():
    return [
        genai.types.Tool(
            function_declarations=[
                genai.types.FunctionDeclaration(
                    name="create_new_tool",
                    description="Creates a new Python module for a tool.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "module_name": {"type": "string"},
                            "code_content": {"type": "string"},
                        },
                        "required": ["module_name", "code_content"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="register_tool_module",
                    description="Registers a new tool module in the system.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "module_name": {"type": "string"},
                        },
                        "required": ["module_name"],
                    },
                ),
            ]
        )
    ]

library = {
    "create_new_tool": create_new_tool_task,
    "register_tool_module": register_tool_module_task,
}
