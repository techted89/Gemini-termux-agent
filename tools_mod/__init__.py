from . import core, web, file_ops, memory, database, learning, display
from .memory import execute_memory_tool
from .database import execute_database_tool
from .display import display_image_task
from .learning import learn_repo_task, learn_directory_task, learn_url_task
from utils.file_system import save_to_file

def get_all_tool_definitions():
    """
    Aggregate and return a flat list of tool definitions from both modern and legacy modules.
    
    Returns:
        list: Tool definitions collected from core, web, file_ops, learning, memory, database, and display. Each item may be a Tool object or a dict.
    """
    all_tools = []

    # Modern Modules (Return List[genai.types.Tool])
    all_tools.extend(core.tool_definitions())
    all_tools.extend(web.tool_definitions())
    all_tools.extend(file_ops.tool_definitions())
    all_tools.extend(learning.tool_definitions())

    # Legacy Modules (Return List[Dict] or List[Tool])
    all_tools.extend(memory.tool_definitions())
    all_tools.extend(database.tool_definitions())
    all_tools.extend(display.tool_definitions())

    return all_tools

# Export as variable and function
tool_definitions_list = get_all_tool_definitions()

def tool_definitions():
    """
    Provide a cached list of all tool definitions available in the module.
    
    Returns:
        list: The precomputed list of tool definition dictionaries aggregated from modern and legacy modules.
    """
    return tool_definitions_list

def execute_tool(name, args):
    """
    Dispatches and runs a registered tool identified by name using the provided arguments.
    
    Parameters:
        name (str): Name of the tool to execute.
        args (dict): Mapping of keyword arguments to pass to the tool.
    
    Returns:
        The result returned by the invoked tool, or the string "Tool {name} not found." when no matching tool exists.
    """
    # 1. Modern Library Lookup
    if hasattr(core, 'library') and name in core.library:
        return core.library[name](**args)

    if hasattr(web, 'library') and name in web.library:
        return web.library[name](**args)

    if hasattr(file_ops, 'library') and name in file_ops.library:
        return file_ops.library[name](**args)

    # 2. Legacy / Special Cases

    # Memory Tools
    # Dynamic check against definitions
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
        return learn_directory_task(args.get('path'))
    elif name == "learn_url":
        return learn_url_task(args.get('url'))

    # Display Tools
    if name == "display_image":
        return display_image_task(args.get('path'))

    # Backward Compatibility
    if name == "save_to_file":
        return save_to_file(args.get('filename'), args.get('content'))

    return f"Tool {name} not found."