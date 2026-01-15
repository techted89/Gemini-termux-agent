import sys
import os
import time
import hashlib
import chromadb
from chromadb.config import Settings
import config
from pathlib import Path

try:
    import pysqlite3
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except ImportError:
    pass

import logging

logger = logging.getLogger(__name__)

def get_db_client():
    """Initializes and returns the ChromaDB client based on config."""
    provider = getattr(config, "CHROMA_CLIENT_PROVIDER", "local")

    if provider == "http":
        logger.info(f"Initializing ChromaDB HttpClient with host={config.CHROMA_HOST}, port={config.CHROMA_PORT}")
        return chromadb.HttpClient(host=config.CHROMA_HOST, port=config.CHROMA_PORT)
    else:
        # Default to local, persistent client
        db_path = getattr(config, "CHROMA_DB_PATH", "chroma_db")
        os.makedirs(db_path, exist_ok=True)
        logger.info(f"Initializing ChromaDB PersistentClient with path={db_path}")
        return chromadb.PersistentClient(path=db_path)

db_client = get_db_client()

def get_relevant_history(query, n_results=15):
    try:
        collection = db_client.get_or_create_collection("agent_memory")
        results = collection.query(query_texts=[query], n_results=n_results)
        return results['documents'][0] if results['documents'] else []
    except Exception: return []

def get_relevant_context(query, n_results=5):
    try:
        collection = db_client.get_or_create_collection("agent_memory")
        results = collection.query(query_texts=[query], n_results=n_results)
        return "\n".join(results['documents'][0]) if results['documents'] else ""
    except Exception: return ""

def store_conversation_turn(user_query, assistant_response, user_id):
    try:
        collection = db_client.get_or_create_collection("agent_memory")
        doc_id = f"turn_{int(time.time())}"
        collection.add(
            documents=[f"User: {user_query}\nAssistant: {assistant_response}"],
            metadatas=[{"user_id": user_id, "timestamp": time.time()}],
            ids=[doc_id]
        )
    except Exception as e: print(f"⚠️ DB Store Error: {e}")

def search_and_delete_history(query_text):
    try:
        collection = db_client.get_or_create_collection("agent_memory")
        results = collection.query(query_texts=[query_text], n_results=10)
        if results['ids'] and len(results['ids'][0]) > 0:
            collection.delete(ids=results['ids'][0])
            return f"✅ Deleted {len(results['ids'][0])} history entries."
        return "ℹ️ No matching history found."
    except Exception: return "❌ Delete error."

def store_embedding(text, metadata, collection_name="agent_learning"):
    try:
        collection = db_client.get_or_create_collection(collection_name)
        doc_id = hashlib.md5(text.encode()).hexdigest()
        collection.upsert(documents=[text], metadatas=[metadata], ids=[doc_id])
        return True
    except Exception: return False

def query_embeddings(query_text, n_results=10, collection_name="agent_learning"):
    try:
        collection = db_client.get_or_create_collection(collection_name)
        return collection.query(query_texts=[query_text], n_results=n_results, include=["documents", "metadatas", "distances"])
    except Exception: return None

def search_and_delete_knowledge(query_text, collection_name="agent_learning"):
    try:
        collection = db_client.get_or_create_collection(collection_name)
        results = collection.query(query_texts=[query_text], n_results=10)
        if results['ids'] and len(results['ids'][0]) > 0:
            collection.delete(ids=results['ids'][0])
            return "✅ Knowledge deleted."
        return "ℹ️ Not found."
    except Exception: return "❌ Delete error."

def update_embedding(doc_id, text=None, metadata=None, collection_name="agent_learning"):
    try:
        collection = db_client.get_or_create_collection(collection_name)
        collection.update(ids=[doc_id], documents=[text] if text else None, metadatas=[metadata] if metadata else None)
        return True
    except Exception: return False

def get_embedding(doc_id, collection_name="agent_learning"):
    try: return db_client.get_collection(collection_name).get(ids=[doc_id])
    except Exception: return None

def get_available_metadata_sources(collection_name="agent_learning"):
    try:
        collection = db_client.get_or_create_collection(collection_name)
        results = collection.get(include=["metadatas"])
        return list(set(m.get('source') for m in results['metadatas'] if m.get('source'))) if results['metadatas'] else []
    except Exception: return []

def get_all_collections():
    try: return db_client.list_collections()
    except Exception: return []

def get_collection_count(collection_name="agent_memory"):
    try: return db_client.get_collection(collection_name).count()
    except: return 0

def delete_embeddings(collection_name="agent_learning"):
    try: db_client.delete_collection(collection_name)
    except Exception: pass