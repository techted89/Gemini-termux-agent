import google.genai as genai
from google.genai import types as genai_types
from utils.database import (
    get_available_metadata_sources,
    delete_by_metadata,
    query_embeddings,
    delete_embeddings,
)


def list_knowledge_task():
    """
    Lists all unique sources (files/URLs) currently stored in the knowledge base.
    """
    sources = get_available_metadata_sources("agent_learning")
    if not sources:
        return "Knowledge base is empty."
    return "Learned Sources:\n" + "\n".join(f"- {s}" for s in sorted(sources))


def delete_knowledge_task(source):
    """
    Deletes all knowledge associated with a specific source.
    """
    if delete_by_metadata("source", source, "agent_learning"):
        return f"Successfully deleted knowledge from source: {source}"
    return f"Failed to delete knowledge from source: {source}"


def search_knowledge_task(query):
    """
    Searches the knowledge base for a specific query.
    """
    results = query_embeddings(query, n_results=5, collection_name="agent_learning")
    if not results or not results["documents"] or not results["documents"][0]:
        return "No relevant knowledge found."

    output = "Search Results:\n"
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        source = meta.get("source", "Unknown")
        output += f"---\nSource: {source}\nContent: {doc[:200]}...\n"
    return output


def clear_knowledge_task():
    """
    Clears the entire knowledge base.
    """
    delete_embeddings("agent_learning")
    return "Knowledge base cleared."


def tool_definitions():
    return [
        genai_types.Tool(
            function_declarations=[
                genai_types.FunctionDeclaration(
                    name="list_knowledge",
                    description="List all sources (files/URLs) currently in the knowledge base.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={},
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="delete_knowledge",
                    description="Delete all knowledge associated with a specific source (file path or URL).",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "source": genai_types.Schema(
                                type=genai_types.Type.STRING,
                                description="The source path or URL to delete.",
                            )
                        },
                        required=["source"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="search_knowledge",
                    description="Search the knowledge base for information.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "query": genai_types.Schema(
                                type=genai_types.Type.STRING,
                                description="The search query.",
                            )
                        },
                        required=["query"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="clear_knowledge",
                    description="Clear the entire knowledge base. Use with caution.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={},
                    ),
                ),
            ]
        )
    ]
