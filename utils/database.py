import chromadb
from sklearn.metrics.pairwise import cosine_similarity
from urllib.parse import urljoin, urlparse
from utils.commands import user_confirm
import config
import google.genai as genai
from google.genai import types
import numpy as np

client = genai.Client(api_key=config.API_KEY)


# --- Embedding ---
EMBEDDING_MODEL = "models/embedding-001"

# --- ChromaDB ---
chroma_client = chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)
collection = chroma_client.get_or_create_collection(name="gemini_rag_collection")
conversation_history_collection = chroma_client.get_or_create_collection(
    name="conversation_history"
)


def get_embedding(text):
    """
    Generates an embedding for the given text.
    """
    if not text.strip():
        print("Attempted to embed an empty string.")
        return None

    try:
        # The API can handle lists of texts, but we'll send one at a time.
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            content=text,
            task_type=types.TaskType.RETRIEVAL_DOCUMENT,
        )
        return result["embedding"]
    except Exception as e:
        print(f"An error occurred during embedding: {e}")
        return None


def store_embedding(text, source, text_type="code"):
    """
    Stores the embedding of a text segment in ChromaDB.
    """
    if not text.strip():
        return

    embedding = get_embedding(text)
    if embedding:
        # ChromaDB requires a unique ID for each entry.
        # We can generate a simple one based on the source and a hash of the text.
        doc_id = f"{source}-{hash(text)}"
        collection.add(
            documents=[text],
            embeddings=[embedding],
            metadatas=[{"source": source, "type": text_type}],
            ids=[doc_id],
        )


def get_relevant_context(
    query, n_results=10, where_filter=None, lambda_mult=0.5, mmr_threshold=0.5
):
    """
    Retrieves the most relevant context from ChromaDB using MMR for diversity.
    """
    query_embedding = get_embedding(query)
    if not query_embedding:
        return ""

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results * 5,
        where=where_filter,
        include=["documents", "embeddings"],
    )

    if not results or not results["documents"]:
        return ""

    docs = results["documents"][0]
    embeddings = np.array(results["embeddings"][0])

    if not docs:
        return ""

    # MMR algorithm
    selected_indices = []
    if docs:
        remaining_indices = list(range(len(docs)))

        # First, add the most relevant document
        most_relevant_idx = remaining_indices[0]
        selected_indices.append(most_relevant_idx)
        remaining_indices.remove(most_relevant_idx)

        while remaining_indices and len(selected_indices) < n_results:
            mmr_scores = []
            for i in remaining_indices:
                similarity_to_query = cosine_similarity(
                    [query_embedding], [embeddings[i]]
                )[0][0]
                max_similarity_to_selected = 0
                if selected_indices:
                    selected_embeddings = embeddings[selected_indices]
                    similarities = cosine_similarity(
                        [embeddings[i]], selected_embeddings
                    )[0]
                    max_similarity_to_selected = np.max(similarities)

                mmr_score = (
                    lambda_mult * similarity_to_query
                    - (1 - lambda_mult) * max_similarity_to_selected
                )
                mmr_scores.append((mmr_score, i))

            if not mmr_scores:
                break

            # Select the document with the highest MMR score
            best_score, best_idx = max(mmr_scores, key=lambda x: x[0])
            if best_score < mmr_threshold:
                break

            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)

    # Return the selected documents in the order they were selected
    selected_docs = [docs[i] for i in selected_indices]
    return "\n---\n".join(selected_docs)


def get_available_metadata_sources():
    """
    Retrieves all unique 'source' values from the collection's metadata.
    """
    try:
        # get() with no IDs/where filter will return all items.
        # We only need the metadata.
        all_items = collection.get(include=["metadatas"])
        sources = {
            metadata["source"]
            for metadata in all_items["metadatas"]
            if "source" in metadata
        }
        return sorted(list(sources))
    except Exception as e:
        print(f"Error retrieving metadata sources: {e}")
        return []


def store_conversation_turn(user_query, model_response, user_id):
    """
    Stores a turn of the conversation in a separate ChromaDB collection.
    """
    turn_text = f"User: {user_query}\nModel: {model_response}"
    embedding = get_embedding(turn_text)
    if embedding:
        turn_id = f"{user_id}-{hash(turn_text)}"
        conversation_history_collection.add(
            documents=[turn_text],
            embeddings=[embedding],
            metadatas=[{"user_id": user_id}],
            ids=[turn_id],
        )


def get_relevant_history(query, user_id, n_results=3):
    """
    Retrieves relevant conversation history for the current query.
    """
    query_embedding = get_embedding(query)
    if not query_embedding:
        return ""

    results = conversation_history_collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        where={"user_id": user_id},
    )

    if not results or not results["documents"]:
        return ""

    # Return the documents in chronological order (oldest first) as they are retrieved
    # by relevance (most relevant first).
    return "\n---\n".join(reversed(results["documents"][0]))


def search_and_delete_knowledge(query=None, source=None, ids=None, confirm=False):
    """
    Searches for and optionally deletes knowledge documents.
    """
    where_filter = {"source": source} if source else {}
    if query:
        query_embedding = get_embedding(query)
        if not query_embedding:
            return "Could not generate embedding for query."
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
            where=where_filter,
            include=["metadatas", "documents"],
        )
        ids_to_delete = results["ids"][0]
        if ids_to_delete and (confirm or user_confirm(f"Delete {len(ids_to_delete)} documents?")):
            collection.delete(ids=ids_to_delete)
            return f"Deleted {len(ids_to_delete)} documents."
        elif ids_to_delete:
            return "Deletion cancelled."
        else:
            return "No documents found to delete."
    elif ids:
        if confirm or user_confirm(f"Delete {len(ids)} documents?"):
            collection.delete(ids=ids)
            return f"Deleted {len(ids)} documents."
        else:
            return "Deletion cancelled."
    else:
        results = collection.get(where=where_filter, include=["metadatas", "documents"])

    return "\n".join(
        [
            f"ID: {id}\nSource: {meta['source']}\nContent: {doc}\n"
            for id, meta, doc in zip(
                results["ids"], results["metadatas"], results["documents"]
            )
        ]
    )


def search_and_delete_history(query, role=None, ids=None, confirm=False):
    """
    Searches for and optionally deletes conversation history.
    """
    where_filter = {"role": role} if role else {}
    if query:
        query_embedding = get_embedding(query)
        if not query_embedding:
            return "Could not generate embedding for query."
        results = conversation_history_collection.query(
            query_embeddings=[query_embedding],
            n_results=10,
            where=where_filter,
            include=["metadatas", "documents"],
        )
        ids_to_delete = results["ids"][0]
        if ids_to_delete and (confirm or user_confirm(f"Delete {len(ids_to_delete)} history entries?")):
            conversation_history_collection.delete(ids=ids_to_delete)
            return f"Deleted {len(ids_to_delete)} history entries."
        elif ids_to_delete:
            return "Deletion cancelled."
        else:
            return "No history entries found to delete."
    elif ids:
        if confirm or user_confirm(f"Delete {len(ids)} history entries?"):
            conversation_history_collection.delete(ids=ids)
            return f"Deleted {len(ids)} history entries."
        else:
            return "Deletion cancelled."
    else:
        results = conversation_history_collection.get(
            where=where_filter, include=["metadatas", "documents"]
        )

    return "\n".join(
        [
            f"ID: {id}\nUser ID: {meta['user_id']}\nContent: {doc}\n"
            for id, meta, doc in zip(
                results["ids"], results["metadatas"], results["documents"]
            )
        ]
    )
