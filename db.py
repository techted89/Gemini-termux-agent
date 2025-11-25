import chromadb
import sys
import google.generativeai as genai
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from config import PROJECT_CONTEXT_IGNORE, CHROMA_HOST

try:
    if not CHROMA_HOST:
        print("Error: CHROMA_HOST not set")
        sys.exit(1)
    client = chromadb.HttpClient(host=CHROMA_HOST, port=8000)
    knowledge_collection = client.get_or_create_collection(name="knowledge")
    conversation_history_collection = client.get_or_create_collection(
        name="conversation_history"
    )
except Exception as e:
    print(f"DB Connection Failed: {e}")
    # Consider sys.exit(1) here if DB connection is critical for the whole script


def get_embedding(text, task_type="RETRIEVAL_DOCUMENT"):
    if not text.strip():
        return None
    try:
        res = genai.embed_content(
            model="models/text-embedding-004", content=text[:10000], task_type=task_type
        )
        return res["embedding"]
    except Exception as e: # Changed bare except to Exception
        print(f"Error getting embedding: {e}") # Added specific error logging
        return None


def learn_file_content(filepath):
    try:
        p = Path(filepath)
        if not p.is_file():
            return
        content = p.read_text(encoding="utf-8", errors="ignore")
        if len(content) > 15000 or not content.strip():
            return
        emb = get_embedding(content)
        if emb:
            knowledge_collection.upsert(
                embeddings=[emb],
                documents=[content],
                metadatas=[{"source": str(p.resolve())}],
                ids=[str(p.resolve())],
            )
            print(".", end="", flush=True)
    except Exception: # Changed bare except to Exception
        pass


def learn_directory(directory_path):
    print(f"Learning: {directory_path}", end="", flush=True)
    for p in Path(directory_path).rglob("*"):
        if any(x in p.parts for x in PROJECT_CONTEXT_IGNORE):
            continue
        if p.is_file() and p.suffix in [".py", ".js", ".txt", ".md"]:
            learn_file_content(p)
    print("\nDone.") # Fixed the syntax error here


def learn_url(url):
    try:
        print(f"Learning URL: {url}")
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        text = BeautifulSoup(res.text, "html.parser").get_text(
            separator=" ", strip=True
        )[:15000]
        emb = get_embedding(text)
        if emb:
            knowledge_collection.upsert(
                embeddings=[emb],
                documents=[text],
                metadatas=[{"source": url, "type": "url"}],
                ids=[url],
            )
            print(f"Learned URL: {url}") # Added confirmation print
    except Exception as e:
        print(f"Error learning URL {url}: {e}") # Enhanced error message


def get_relevant_context(prompt, n_results=5):
    try:
        emb = get_embedding(prompt, task_type="RETRIEVAL_QUERY")
        if not emb:
            return ""
        res = knowledge_collection.query(query_embeddings=[emb], n_results=n_results)
        if not res["documents"] or not res["documents"][0]:
            return ""
        ctx = "--- RELEVANT CONTEXT ---\n"
        for i, doc in enumerate(res["documents"][0]):
            source = res['metadatas'][0][i].get('source', 'Unknown') # Safely get source
            ctx += f"Source: {source}\nContent: {doc[:500]}...\n\n"
        return ctx
    except Exception as e: # Changed bare except to Exception
        print(f"Error retrieving context: {e}") # Added specific error logging
        return ""


def delete_knowledge(ids=None, where=None):
    """
    Deletes entries from the knowledge collection.
    Args:
        ids (list, optional): List of document IDs to delete.
        where (dict, optional): A ChromaDB filter dictionary to specify documents by metadata.
                                E.g., {"source": "some_path.py"}.
    Returns:
        bool: True if deletion was attempted, False if no IDs or filters were provided or an error occurred.
    """
    if not ids and not where:
        print("Warning: No IDs or 'where' clause provided for knowledge deletion.")
        return False
    try:
        knowledge_collection.delete(ids=ids, where=where)
        print(f"Knowledge deleted. IDs: {ids if ids else 'N/A'}, Where: {where if where else 'N/A'}")
        return True
    except Exception as e:
        print(f"Error deleting knowledge: {e}")
        return False


def delete_conversation_history(ids=None, where=None):
    """
    Deletes entries from the conversation history collection.
    Args:
        ids (list, optional): List of document IDs to delete.
        where (dict, optional): A ChromaDB filter dictionary to specify documents by metadata.
                                E.g., {"role": "user"}.
    Returns:
        bool: True if deletion was attempted, False if no IDs or filters were provided or an error occurred.
    """
    if not ids and not where:
        print("Warning: No IDs or 'where' clause provided for conversation history deletion.")
        return False
    try:
        conversation_history_collection.delete(ids=ids, where=where)
        print(f"Conversation history deleted. IDs: {ids if ids else 'N/A'}, Where: {where if where else 'N/A'}")
        return True
    except Exception as e:
        print(f"Error deleting conversation history: {e}")
        return False


def search_and_delete_knowledge(query, source=None, ids=None, confirm=True):
    """
    Searches for and deletes entries from the knowledge collection.
    """
    where_clause = {}
    if source:
        where_clause["source"] = source

    results = knowledge_collection.get(where=where_clause, ids=ids)
    if not results["ids"]:
        return "No knowledge found to delete."

    if confirm and not user_confirm(f"Delete {len(results['ids'])} knowledge entries?"):
        return "Deletion cancelled."

    knowledge_collection.delete(ids=results["ids"])
    return f"Deleted {len(results['ids'])} knowledge entries."


def search_and_delete_history(query, role=None, ids=None, confirm=True):
    """
    Searches for and deletes entries from the conversation history collection.
    """
    where_clause = {}
    if role:
        where_clause["role"] = role

    results = conversation_history_collection.get(where=where_clause, ids=ids)
    if not results["ids"]:
        return "No history found to delete."

    if confirm and not user_confirm(f"Delete {len(results['ids'])} history entries?"):
        return "Deletion cancelled."

    conversation_history_collection.delete(ids=results["ids"])
    return f"Deleted {len(results['ids'])} history entries."



