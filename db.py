import chromadb
import sys
import google.generativeai as genai
from pathlib import Path
import requests
import uuid
import time
import numpy as np
from bs4 import BeautifulSoup
from config import PROJECT_CONTEXT_IGNORE, CHROMA_HOST
from helpers import user_confirm

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


def learn_file_content(filepath, content=None, metadata=None):
    try:
        p = Path(filepath)
        if content is None:
            if not p.is_file():
                return
            content = p.read_text(encoding="utf-8", errors="ignore")

        if len(content) > 15000 or not content.strip():
            return

        emb = get_embedding(content)
        if emb:
            # Use provided metadata or create a default
            meta = metadata or {"source": str(p.resolve())}
            # Ensure 'source' is in meta
            if "source" not in meta:
                meta["source"] = str(p.resolve())

            # Create a unique ID for each chunk, e.g., by combining path and a hash of content
            chunk_id = f"{str(p.resolve())}_{hash(content)}"

            knowledge_collection.upsert(
                embeddings=[emb],
                documents=[content],
                metadatas=[meta],
                ids=[chunk_id],
            )
            print(".", end="", flush=True)
    except Exception as e:
        print(f"Error learning file content for {filepath}: {e}")


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


def get_relevant_context(prompt, n_results=5, where_filter=None, lambda_mult=0.7):
    """
    Retrieves relevant and diverse context from the knowledge base using MMR.
    """
    try:
        query_embedding = get_embedding(prompt, task_type="RETRIEVAL_QUERY")
        if not query_embedding:
            return ""

        # 1. Retrieve a larger pool of candidates
        fetch_k = n_results * 4
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": fetch_k,
            "include": ["metadatas", "documents", "embeddings"]
        }
        if where_filter:
            query_params["where"] = where_filter

        results = knowledge_collection.query(**query_params)

        if not results["documents"] or not results["documents"][0]:
            return ""

        candidate_embeddings = np.array(results["embeddings"][0])
        query_embedding = np.array(query_embedding)

        # 2. Select the best match first
        similarities = np.dot(candidate_embeddings, query_embedding)
        best_match_idx = np.argmax(similarities)

        selected_indices = [best_match_idx]
        selected_embeddings = [candidate_embeddings[best_match_idx]]

        # 3. Iteratively re-rank and select the rest
        while len(selected_indices) < n_results:
            mmr_scores = []
            remaining_indices = [i for i in range(len(candidate_embeddings)) if i not in selected_indices]

            for i in remaining_indices:
                relevance = similarities[i]
                max_similarity_to_selected = np.max(np.dot(selected_embeddings, candidate_embeddings[i]))
                mmr_score = lambda_mult * relevance - (1 - lambda_mult) * max_similarity_to_selected
                mmr_scores.append((mmr_score, i))

            if not mmr_scores:
                break

            # Select the best MMR score and add to selected
            best_mmr_idx = max(mmr_scores, key=lambda x: x[0])[1]
            selected_indices.append(best_mmr_idx)
            selected_embeddings.append(candidate_embeddings[best_mmr_idx])

        # 4. Format the final context
        filter_str = f" with filter: {where_filter}" if where_filter else ""
        ctx = f"--- RELEVANT CONTEXT (Query: '{prompt}'{filter_str}) ---\n"
        for i in selected_indices:
            source = results['metadatas'][0][i].get('source', 'Unknown')
            ctx += f"Source: {source}\nContent: {results['documents'][0][i][:500]}...\n\n"

        return ctx

    except Exception as e:
        print(f"Error retrieving context with MMR: {e}")
        return ""

def get_available_metadata_sources():
    """
    Retrieves a list of all unique 'source' values from the knowledge collection.

    This is useful for discovering what sources the agent can filter by in its queries.

    Returns:
        list[str]: A list of unique source strings, or an error message.
    """
    try:
        # The 'include=[]' parameter ensures we only fetch metadata
        all_entries = knowledge_collection.get(include=["metadatas"])

        # Using a set to efficiently find unique sources
        unique_sources = set()
        for metadata in all_entries.get("metadatas", []):
            if "source" in metadata:
                unique_sources.add(metadata["source"])

        return list(unique_sources) if unique_sources else "No metadata sources found."

    except Exception as e:
        return f"Error getting metadata sources: {e}"

def store_conversation_turn(user_query, ai_response, user_id="default_user"):
    """
    Stores a single turn of the conversation in the history collection.
    """
    try:
        doc_content = f"User: {user_query}\nAI: {ai_response}"
        embedding = get_embedding(doc_content, task_type="RETRIEVAL_DOCUMENT")
        if not embedding:
            return

        interaction_id = f"msg_{uuid.uuid4()}"
        metadata = {
            "user_id": user_id,
            "session_id": "session_alpha",  # Placeholder for session management
            "timestamp": int(time.time())
        }

        conversation_history_collection.upsert(
            ids=[interaction_id],
            embeddings=[embedding],
            documents=[doc_content],
            metadatas=[metadata]
        )
    except Exception as e:
        print(f"Error storing conversation turn: {e}")

def get_relevant_history(query, user_id, n_results=3):
    """
    Retrieves relevant conversation history for a given user.
    """
    try:
        embedding = get_embedding(query, task_type="RETRIEVAL_QUERY")
        if not embedding:
            return ""

        results = conversation_history_collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            where={"user_id": user_id}
        )

        if not results["documents"] or not results["documents"][0]:
            return ""

        history_context = "--- RELEVANT PAST CONTEXT ---\n"
        for doc in results["documents"][0]:
            history_context += f"{doc}\n---\n"

        return history_context
    except Exception as e:
        print(f"Error retrieving conversation history: {e}")
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



