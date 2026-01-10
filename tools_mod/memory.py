import sys
from utils.database import get_relevant_history, search_and_delete_history

def tool_definitions():
    return [
        {
            "name": "query_memory",
            "description": "Retrieve relevant past conversation history based on a query.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING", "description": "The search term for past conversations"}
                },
                "required": ["query"]
            }
        },
        {
            "name": "delete_memory_entry",
            "description": "Delete specific entries from the conversation history.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING", "description": "Search term to identify entries to delete"}
                },
                "required": ["query"]
            }
        }
    ]

def execute_memory_tool(name, args):
    """
    REQUIRED BY tools_mod/__init__.py
    Executes memory-specific operations.
    """
    if name == "query_memory":
        query = args.get("query")
        results = get_relevant_history(query)
        return results if results else "No relevant memories found."
        
    elif name == "delete_memory_entry":
        query = args.get("query")
        return search_and_delete_history(query)
        
    return f"Memory tool '{name}' not recognized."