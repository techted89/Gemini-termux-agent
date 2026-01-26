import unittest
import sys
import os
import shutil
import time
import hashlib
import atexit

# Set temp db path
# We use a unique path to avoid conflicts
test_db_path = f"chroma_db_test_{int(time.time())}"
os.environ["CHROMA_DB_PATH"] = test_db_path

sys.path.append(os.getcwd())

from utils.database import (
    store_embedding,
    get_embedding,
    delete_embeddings,
    get_collection,
    _collections_cache,
    db_client
)

# Cleanup function to be called at exit
def cleanup_db():
    if os.path.exists(test_db_path):
        try:
            shutil.rmtree(test_db_path)
        except:
            pass

atexit.register(cleanup_db)

class TestDatabaseOptimization(unittest.TestCase):
    def setUp(self):
        self.collection_name = "test_collection"
        # Ensure clean state in cache
        if self.collection_name in _collections_cache:
            del _collections_cache[self.collection_name]
        # Ensure clean state in DB
        try:
            db_client.delete_collection(self.collection_name)
        except:
            pass

    def tearDown(self):
        try:
            db_client.delete_collection(self.collection_name)
        except:
            pass
        if self.collection_name in _collections_cache:
            del _collections_cache[self.collection_name]
        # Do NOT delete the DB directory here as db_client is persistent across tests

    def test_caching_behavior(self):
        # 1. Ensure cache is empty for this collection
        self.assertNotIn(self.collection_name, _collections_cache)

        # 2. Store embedding (should populate cache)
        success = store_embedding("test text", {"source": "test"}, self.collection_name)
        self.assertTrue(success, "store_embedding failed")

        # 3. Verify collection is in cache
        self.assertIn(self.collection_name, _collections_cache)
        cached_collection = _collections_cache[self.collection_name]

        # 4. Call get_collection again, should return same object
        coll2 = get_collection(self.collection_name)
        self.assertIs(cached_collection, coll2)

        # 5. Delete collection via delete_embeddings (which should update cache)
        delete_embeddings(self.collection_name)
        self.assertNotIn(self.collection_name, _collections_cache)

    def test_store_and_retrieve(self):
        text = "hello world"
        success = store_embedding(text, {"source": "test"}, self.collection_name)
        self.assertTrue(success, "store_embedding failed")

        doc_id = hashlib.md5(text.encode()).hexdigest()

        # Retrieve
        result = get_embedding(doc_id, self.collection_name)

        self.assertIsNotNone(result)
        self.assertEqual(result['ids'][0], doc_id)
        self.assertEqual(result['documents'][0], text)

if __name__ == "__main__":
    unittest.main()
