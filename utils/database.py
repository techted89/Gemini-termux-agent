import chromadb
from chromadb.utils import embedding_functions
from bs4 import BeautifulSoup
from sklearn.metrics.pairwise import cosine_similarity
import requests
import os
from urllib.parse import urljoin, urlparse
from utils.commands import user_confirm
import config
import google.generativeai as genai

genai.configure(api_key=config.API_KEY)

client = chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


knowledge_collection = client.get_or_create_collection(
    name="knowledge",
    embedding_function=embedding_function,
    metadata={"hnsw:space": "cosine"},
)
history_collection = client.get_or_create_collection(
    name="history",
    embedding_function=embedding_function,
    metadata={"hnsw:space": "cosine"},
)


def learn_file_content(filepath, content=None, metadata=None):
    if not content:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return f"Error reading file {filepath}: {e}"

    if not metadata:
        metadata = {"source": filepath}
    elif "source" not in metadata:
        metadata["source"] = filepath

    knowledge_collection.add(documents=[content], metadatas=[metadata], ids=[filepath])
    return f"Learned content from {filepath}."


def learn_directory(directory_path, ignore_patterns=None):
    if ignore_patterns is None:
        ignore_patterns = config.PROJECT_CONTEXT_IGNORE

    for root, _, files in os.walk(directory_path):
        for file in files:
            if any(file.endswith(p) for p in ignore_patterns):
                continue
            filepath = os.path.join(root, file)
            learn_file_content(filepath)
    return f"Finished learning from directory: {directory_path}."


def is_valid_url(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def fetch_and_parse_url(url, visited_urls=None):
    if visited_urls is None:
        visited_urls = set()
    if url in visited_urls:
        return ""
    visited_urls.add(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()

        text = " ".join(soup.stripped_strings)

        links = {
            urljoin(url, a["href"])
            for a in soup.find_all("a", href=True)
            if is_valid_url(urljoin(url, a["href"]))
            and urlparse(urljoin(url, a["href"])).netloc == urlparse(url).netloc
        }

        return text, links
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return "", set()


def learn_url(url, depth=1):
    text, links = fetch_and_parse_url(url)
    if text:
        knowledge_collection.add(
            documents=[text], metadatas=[{"source": url}], ids=[url]
        )
    if depth > 0:
        for link in links:
            learn_url(link, depth - 1)
    return f"Learned content from {url}."


def get_relevant_context(query, n_results=5, where_filter=None):
    query_embedding = embedding_function([query])[0]

    # Initial query to get a larger pool of candidates
    candidate_results = knowledge_collection.query(
        query_embeddings=[query_embedding],
        n_results=max(n_results * 5, 20),  # Fetch more candidates for MMR
        where=where_filter,
        include=["embeddings", "documents"],
    )

    candidate_embeddings = candidate_results["embeddings"][0]
    candidate_documents = candidate_results["documents"][0]
    candidate_ids = candidate_results["ids"][0]

    if not candidate_documents:
        return []

    # MMR implementation
    selected_indices = []
    # The first document is the most relevant one
    selected_indices.append(0)
    remaining_indices = list(range(1, len(candidate_documents)))

    lambda_mult = 0.5  # Balances relevance and diversity

    while len(selected_indices) < min(n_results, len(candidate_documents)):
        max_mmr = -float("inf")
        best_next_idx = -1

        for i in remaining_indices:
            relevance_to_query = (
                1
                - cosine_similarity(
                    [query_embedding], [candidate_embeddings[i]]
                )[0][0]
            )
            max_similarity_to_selected = 0
            if selected_indices:
                selected_docs_embeddings = [
                    candidate_embeddings[j] for j in selected_indices
                ]
                similarity_to_selected = 1 - cosine_similarity(
                    [candidate_embeddings[i]], selected_docs_embeddings
                )
                max_similarity_to_selected = max(similarity_to_selected[0])

            mmr_score = (
                lambda_mult * relevance_to_query
                - (1 - lambda_mult) * max_similarity_to_selected
            )

            if mmr_score > max_mmr:
                max_mmr = mmr_score
                best_next_idx = i

        if best_next_idx != -1:
            selected_indices.append(best_next_idx)
            remaining_indices.remove(best_next_idx)
        else:
            break

    return [candidate_documents[i] for i in selected_indices]


def get_relevant_history(query, user_id, n_results=3):
    results = history_collection.query(
        query_texts=[query], n_results=n_results, where={"user_id": user_id}
    )
    # Reconstruct conversation turns from the retrieved documents
    history_context = ""
    for doc in reversed(results["documents"][0]):
        # Assuming the format "user: <...>\nmodel: <...>"
        history_context += doc + "\n"
    return history_context


def store_conversation_turn(user_input, model_response, user_id):
    turn_text = f"user: {user_input}\nmodel: {model_response}"
    turn_id = f"{user_id}_{len(history_collection.get()['ids']) + 1}"
    history_collection.add(
        documents=[turn_text], metadatas=[{"user_id": user_id}], ids=[turn_id]
    )


def search_and_delete_knowledge(query=None, source=None, ids=None, confirm=True):
    where_filter = {}
    if source:
        where_filter["source"] = source

    if query:
        results = knowledge_collection.query(
            query_texts=[query], where=where_filter, n_results=10
        )
        ids_to_delete = results["ids"][0]
    elif ids:
        ids_to_delete = ids
    else:
        return "Either a query or a list of IDs must be provided."

    if not ids_to_delete:
        return "No matching documents found to delete."

    print("Documents to be deleted:")
    for i, doc_id in enumerate(ids_to_delete):
        print(f"{i+1}. {doc_id}")

    if confirm and not user_confirm("Proceed with deletion?"):
        return "Deletion cancelled."

    knowledge_collection.delete(ids=ids_to_delete)
    return f"Deleted {len(ids_to_delete)} documents."


def search_and_delete_history(query=None, role=None, ids=None, confirm=True):
    where_filter = {}
    if role:
        where_filter["role"] = role

    if query:
        results = history_collection.query(
            query_texts=[query], where=where_filter, n_results=10
        )
        ids_to_delete = results["ids"][0]
    elif ids:
        ids_to_delete = ids
    else:
        return "Either a query or a list of IDs must be provided."

    if not ids_to_delete:
        return "No matching history entries found to delete."

    print("History entries to be deleted:")
    for i, doc_id in enumerate(ids_to_delete):
        print(f"{i+1}. {doc_id}")

    if confirm and not user_confirm("Proceed with deletion?"):
        return "Deletion cancelled."

    history_collection.delete(ids=ids_to_delete)
    return f"Deleted {len(ids_to_delete)} history entries."


def get_available_metadata_sources():
    metadata = knowledge_collection.get(include=["metadatas"])
    sources = {meta["source"] for meta in metadata["metadatas"]}
    return list(sources)
