from .memory import tool_definitions as memory_tools, execute_memory_tool
from .database import tool_definitions as database_tools, execute_database_tool
from .code_tools import tool_definitions as code_tools, execute_code_tool

def get_all_tool_definitions():
    """
    GitHub Logic: Returns a flat list of all tool dictionaries.
    """
    all_tools = []
    # We call these because the sub-modules define them as functions
    all_tools.extend(memory_tools())
    all_tools.extend(database_tools())
    all_tools.extend(code_tools())
    return all_tools

# 1. Export as a list (for logic that expects a mapping/list)
tool_definitions_list = get_all_tool_definitions()

# 2. Export as a variable named tool_definitions to satisfy 'callable' checks
# This allows tool_definitions() to work if it's a function, 
# or tool_definitions to work if it's a list.
def tool_definitions():
    return tool_definitions_list

def execute_tool(name, args):
    # Flatten checks to avoid 'list' object attribute errors
    if name in [t['name'] for t in memory_tools()]:
        return execute_memory_tool(name, args)
    if name in [t['name'] for t in database_tools()]:
        return execute_database_tool(name, args)
    if name in [t['name'] for t in code_tools()]:
        return execute_code_tool(name, args)
    return f"Tool {name} not found."