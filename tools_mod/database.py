from utils.database import (
    search_and_delete_history,
    search_and_delete_knowledge,
    get_available_metadata_sources,
    get_collection_count
)

def tool_definitions():
    return [
        {
            "name": "manage_knowledge",
            "description": "Search and delete specific knowledge or history entries.",
            "parameters": {
                "type": "OBJECT",
                "properties": {
                    "action": {"type": "STRING", "enum": ["delete_history", "delete_knowledge"]},
                    "query": {"type": "STRING", "description": "The search term to match for deletion"}
                },
                "required": ["action", "query"]
            }
        },
        {
            "name": "get_db_stats",
            "description": "Get statistics about the memory and knowledge base.",
            "parameters": {"type": "OBJECT", "properties": {}}
        }
    ]

def execute_database_tool(name, args):
    if name == "manage_knowledge":
        action = args.get("action")
        query = args.get("query")
        if action == "delete_history":
            return search_and_delete_history(query)
        elif action == "delete_knowledge":
            return search_and_delete_knowledge(query)
    elif name == "get_db_stats":
        return {
            "history_count": get_collection_count("agent_memory"),
            "knowledge_count": get_collection_count("agent_learning"),
            "sources": get_available_metadata_sources()
        }
    return "Unknown database tool action."