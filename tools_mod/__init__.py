from .memory import tool_definitions as memory_tools, execute_memory_tool
from .database import tool_definitions as database_tools, execute_database_tool
from .learning import (
    tool_definitions as learning_tools,
    learn_repo_task,
    learn_directory_task,
    learn_url_task,
)
from .file_ops import tool_definitions as file_op_tools, stat_task, chmod_task
from .knowledge import (
    tool_definitions as knowledge_tools,
    list_knowledge_task,
    delete_knowledge_task,
    search_knowledge_task,
    clear_knowledge_task,
)
from utils.file_system import save_to_file
from .display import tool_definitions as display_tools, display_image_task


def get_all_tool_definitions():
    """
    GitHub Logic: Returns a flat list of all tool dictionaries.
    """
    all_tools = []
    # We call these because the sub-modules define them as functions
    all_tools.extend(memory_tools())
    all_tools.extend(database_tools())
    all_tools.extend(learning_tools())
    all_tools.extend(knowledge_tools())
    all_tools.extend(file_op_tools())
    all_tools.extend(display_tools())
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
    if name in [t["name"] for t in memory_tools()]:
        return execute_memory_tool(name, args)
    if name in [t["name"] for t in database_tools()]:
        return execute_database_tool(name, args)
    if name in [t["name"] for t in learning_tools()]:
        if name == "learn_repo":
            return learn_repo_task()
        elif name == "learn_directory":
            return learn_directory_task(args["path"])
        elif name == "learn_url":
            # Handle optional depth argument
            depth = args.get("depth", 0)
            return learn_url_task(args["url"], depth=depth)
    if name in [t["name"] for t in knowledge_tools()]:
        if name == "list_knowledge":
            return list_knowledge_task()
        elif name == "delete_knowledge":
            return delete_knowledge_task(args["source"])
        elif name == "search_knowledge":
            return search_knowledge_task(args["query"])
        elif name == "clear_knowledge":
            return clear_knowledge_task()
    if name in [t["name"] for t in file_op_tools()]:
        if name == "stat":
            return stat_task(args["path"])
        elif name == "chmod":
            return chmod_task(args["path"], args["mode"])
        elif name == "save_to_file":
            return save_to_file(args["filename"], args["content"])
    if name in [t["name"] for t in display_tools()]:
        if name == "display_image":
            return display_image_task(args["path"])
    return f"Tool {name} not found."
