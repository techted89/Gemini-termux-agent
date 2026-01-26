import google.genai as genai
from utils.database import (
    get_available_metadata_sources,
    search_and_delete_knowledge,
    query_embeddings,
    delete_embeddings,
    get_collection_count
)

def list_knowledge_task():
    """Lists available knowledge sources and statistics."""
    sources = get_available_metadata_sources()
    count = get_collection_count("agent_learning")
    if not sources:
        return f"Knowledge base empty (Count: {count})."

    return f"Knowledge Base Stats:\nTotal Documents: {count}\nSources:\n" + "\n".join([f"- {s}" for s in sources])

def delete_knowledge_task(query):
    """Deletes knowledge entries matching the query."""
    return search_and_delete_knowledge(query)

def search_knowledge_task(query):
    """Searches the knowledge base."""
    results = query_embeddings(query)
    if not results or not results['documents']:
        return "No results found."

    output = []
    for i, doc in enumerate(results['documents'][0]):
        meta = results['metadatas'][0][i] if results['metadatas'] else {}
        output.append(f"Source: {meta.get('source', 'Unknown')}\nContent: {doc[:200]}...")
    return "\n---\n".join(output)

def clear_knowledge_task(confirm=False):
    """Clears all knowledge (Dangerous). Requires explicit confirmation."""
    if not confirm:
        return "Operation cancelled. You must explicitly set 'confirm' to True to clear the knowledge base."

    delete_embeddings("agent_learning")
    return "Knowledge base cleared."

def tool_definitions():
    return [
        genai.types.Tool(
            function_declarations=[
                genai.types.FunctionDeclaration(
                    name="list_knowledge",
                    description="Lists available knowledge sources and statistics.",
                    parameters={"type": "object", "properties": {}},
                ),
                genai.types.FunctionDeclaration(
                    name="delete_knowledge",
                    description="Deletes knowledge entries matching a query.",
                    parameters={
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="search_knowledge",
                    description="Searches the knowledge base for relevant content.",
                    parameters={
                        "type": "object",
                        "properties": {"query": {"type": "string"}},
                        "required": ["query"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="clear_knowledge",
                    description="Clears the entire knowledge base.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "confirm": {
                                "type": "boolean",
                                "description": "Must be set to True to execute this destructive action."
                            }
                        },
                        "required": ["confirm"],
                    },
                ),
            ]
        )
    ]

library = {
    "list_knowledge": list_knowledge_task,
    "delete_knowledge": delete_knowledge_task,
    "search_knowledge": search_knowledge_task,
    "clear_knowledge": clear_knowledge_task,
}
