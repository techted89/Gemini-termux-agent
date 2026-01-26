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
    backup_path = init_path + ".bak"

    try:
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Create backup before modification
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)

        # 1. Add Import
        # Check if already imported (more precise check)
        if re.search(rf'\bimport\s+.*\b{re.escape(module_name)}\b', content):
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
        # We assume the user wants to add it to the list.
        # This part relies on string matching which is brittle but necessary here.
        # We append "all_tools.extend(module_name.tool_definitions())"

        def_pattern = r"(    return all_tools)"
        def_insert = f"    all_tools.extend({module_name}.tool_definitions())\n"

        if def_insert not in content:
            content = re.sub(def_pattern, f"{def_insert}\\1", content)

        # 3. Add to execute_tool
        # With the new dynamic loop in __init__.py, we just need to add the module to the list!
        # The list is: modern_modules = [core, web, file_ops, git, nlp, debug_test, tool_creator, knowledge]

        # We look for that list definition.
        list_pattern = r"(modern_modules = \[[^\]]+)(\])"
        # We need to handle multi-line lists.
        match_list = re.search(list_pattern, content, re.DOTALL)
        if match_list:
            current_list = match_list.group(1)
            # Add comma if needed
            new_list_content = f"{current_list}, {module_name}"
            content = content.replace(current_list, new_list_content)
        else:
            # Warn about partial registration
            print(f"Warning: Could not add {module_name} to modern_modules list. Tool definitions registered but execution may fail.")

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
