import time
import os
import shutil
import sys
import uuid

# Set a temp db path
os.environ["CHROMA_DB_PATH"] = "chroma_db_benchmark"

# Import after setting env var
# We need to add the root to sys.path to import utils
sys.path.append(os.getcwd())

from utils.database import store_embedding, db_client

def run_benchmark():
    # Setup
    collection_name = "benchmark_collection"
    # We use a larger number of iterations to make the collection lookup overhead significant compared to cold start
    iterations = 200

    print(f"Running benchmark with {iterations} iterations...")

    start_time = time.time()
    for i in range(iterations):
        text = f"This is a benchmark text number {i} {uuid.uuid4()}"
        metadata = {"source": "benchmark", "index": i}
        store_embedding(text, metadata, collection_name)
    end_time = time.time()

    duration = end_time - start_time
    print(f"Total time: {duration:.4f} seconds")
    print(f"Avg time per call: {duration/iterations:.4f} seconds")

    # Cleanup
    try:
        db_client.delete_collection(collection_name)
    except:
        pass

if __name__ == "__main__":
    try:
        run_benchmark()
    finally:
        if os.path.exists("chroma_db_benchmark"):
            shutil.rmtree("chroma_db_benchmark")
