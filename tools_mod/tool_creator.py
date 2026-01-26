import os
import re
import google.genai as genai
import ast
import logging
import keyword

logger = logging.getLogger(__name__)

def create_new_tool_task(module_name, code_content):
    """
    Creates a new Python module in tools_mod/ with the provided content.
    """
    if not module_name.isidentifier() or keyword.iskeyword(module_name):
        return "Error: Invalid module name. Must be a valid Python identifier and not a keyword."

    filepath = os.path.join("tools_mod", f"{module_name}.py")

    if os.path.exists(filepath):
        return f"Error: Module {module_name} already exists."

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code_content)
        return f"Successfully created {filepath}. Now use register_tool_module('{module_name}') to enable it."
    except Exception as e:
        return f"Error creating tool module: {e}"

class ToolDefinitionVisitor(ast.NodeVisitor):
    def __init__(self, module_name):
        self.module_name = module_name
        self.found = False
        self.modified = False

    def visit_FunctionDef(self, node):
        if node.name == "get_all_tool_definitions":
            # Search for "return all_tools"
            for i, stmt in enumerate(node.body):
                if isinstance(stmt, ast.Return):
                    # Check if it returns "all_tools"
                    if isinstance(stmt.value, ast.Name) and stmt.value.id == "all_tools":
                        # Found it! Insert before this statement.
                        # all_tools.extend(module_name.tool_definitions())
                        new_call = ast.Expr(
                            value=ast.Call(
                                func=ast.Attribute(
                                    value=ast.Name(id="all_tools", ctx=ast.Load()),
                                    attr="extend",
                                    ctx=ast.Load()
                                ),
                                args=[
                                    ast.Call(
                                        func=ast.Attribute(
                                            value=ast.Name(id=self.module_name, ctx=ast.Load()),
                                            attr="tool_definitions",
                                            ctx=ast.Load()
                                        ),
                                        args=[],
                                        keywords=[]
                                    )
                                ],
                                keywords=[]
                            )
                        )
                        node.body.insert(i, new_call)
                        self.modified = True
                        break
        self.generic_visit(node)

def register_tool_module_task(module_name):
    """
    Registers a new tool module in tools_mod/__init__.py using AST for robust insertion.
    """
    if not module_name.isidentifier() or keyword.iskeyword(module_name):
        return "Error: Invalid module name."

    init_path = os.path.join("tools_mod", "__init__.py")
    backup_path = init_path + ".bak"

    try:
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Create backup
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(content)

        # 1. Add Import

        # Let's parse the whole file
        tree = ast.parse(content)

        # Check if already imported
        already_imported = False
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module == ".":
                for alias in node.names:
                    if alias.name == module_name:
                        already_imported = True
                        break

        if already_imported:
             return f"Module {module_name} seems to be already registered."

        # Add import to the first "from . import ..." block found
        import_added = False
        for node in tree.body:
            if isinstance(node, ast.ImportFrom) and node.module == ".":
                node.names.append(ast.alias(name=module_name, asname=None))
                import_added = True
                break

        if not import_added:
            # Prepend import
            new_import = ast.ImportFrom(module=".", names=[ast.alias(name=module_name, asname=None)], level=1)
            tree.body.insert(0, new_import)

        # 2. Modify get_all_tool_definitions using Visitor/Modifier logic
        visitor = ToolDefinitionVisitor(module_name)
        visitor.visit(tree)

        if not visitor.modified:
            return "Error: Could not find 'get_all_tool_definitions' or 'return all_tools' to patch."

        # 3. Modify execute_tool (Regex/String replacement for the list)
        # AST unparse will produce clean code. We can modify the list node if we find it.
        # modern_modules = [...]

        list_modified = False
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == "execute_tool":
                 for subnode in node.body:
                    if isinstance(subnode, ast.Assign):
                        # Check targets
                        for target in subnode.targets:
                            if isinstance(target, ast.Name) and target.id == "modern_modules":
                                if isinstance(subnode.value, ast.List):
                                    # Add module_name to list
                                    subnode.value.elts.append(ast.Name(id=module_name, ctx=ast.Load()))
                                    list_modified = True
                                    break

        if not list_modified:
            logger.warning(f"Could not find 'modern_modules' list in {init_path}. 'execute_tool' registration might be incomplete.")

        # Write back
        new_content = ast.unparse(tree)
        with open(init_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        return f"Successfully registered {module_name}."

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
