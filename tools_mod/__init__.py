from . import core, web, file_ops, memory, database, learning, display, git, nlp, debug_test, tool_creator
from .memory import execute_memory_tool
from .database import execute_database_tool
from .display import display_image_task
from .learning import learn_repo_task, learn_directory_task, learn_url_task

def get_all_tool_definitions():
    """
    Returns a flat list of all tool definitions (Tools or Dicts).
    """
    all_tools = []

    # Modern Modules (Return List[genai.types.Tool])
    all_tools.extend(core.tool_definitions())
    all_tools.extend(web.tool_definitions())
    all_tools.extend(file_ops.tool_definitions())
    all_tools.extend(learning.tool_definitions())
    all_tools.extend(git.tool_definitions())
    all_tools.extend(nlp.tool_definitions())
    all_tools.extend(debug_test.tool_definitions())
    all_tools.extend(tool_creator.tool_definitions())

    # Legacy Modules (Return List[Dict] or List[Tool])
    all_tools.extend(memory.tool_definitions())
    all_tools.extend(database.tool_definitions())
    all_tools.extend(display.tool_definitions())

    return all_tools

def tool_definitions():
    # Dynamically call get_all_tool_definitions each time
    # to support runtime updates (e.g., via tool_creator)
    return get_all_tool_definitions()

def execute_tool(name, args):
    """
    Executes a tool by name with the given arguments.
    """
    # 1. Modern Library Lookup
    # Consolidated loop for cleaner extension
    modern_modules = [
        core, web, file_ops, git, nlp, debug_test, tool_creator
    ]

    for module in modern_modules:
        if hasattr(module, 'library') and name in module.library:
            return module.library[name](**args)

    # 2. Legacy / Special Cases

    # Memory Tools
    memory_tools = [t['name'] for t in memory.tool_definitions() if isinstance(t, dict) and 'name' in t]
    if name in memory_tools:
        return execute_memory_tool(name, args)

    # Database Tools
    database_tools = [t['name'] for t in database.tool_definitions() if isinstance(t, dict) and 'name' in t]
    if name in database_tools:
        return execute_database_tool(name, args)

    # Learning Tools (Direct Mapping)
    if name == "learn_repo":
        return learn_repo_task()
    elif name == "learn_directory":
        path = args.get('path')
        if not path:
            return "Error: 'path' parameter is required for learn_directory."
        return learn_directory_task(path)
    elif name == "learn_url":
        url = args.get('url')
        if not url:
            return "Error: 'url' parameter is required for learn_url."
        return learn_url_task(url)

    # Display Tools
    if name == "display_image":
        path = args.get('path')
        if not path:
            return "Error: 'path' parameter is required for display_image."
        return display_image_task(path)

    return f"Tool {name} not found."
