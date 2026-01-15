import os
from utils.database import store_embeddings
from urllib.parse import urlparse
from utils.chunking import chunk_text
import config


def is_binary_file(filepath, chunk_size=1024):
    """
    Checks if a file is binary by reading a small chunk and checking for null bytes.
    """
    try:
        with open(filepath, "rb") as f:
            chunk = f.read(chunk_size)
            if b"\0" in chunk:
                return True
    except Exception:
        pass  # If we can't read it, assume it's not safe to process as text
    return False


def learn_file_content(file_path, content):
    """
    Learns the content of a single file and stores its embeddings (chunked).
    """
    chunks = chunk_text(content)
    metadatas = []
    for i, chunk in enumerate(chunks):
        metadatas.append({"source": file_path, "chunk_index": i})

    if chunks:
        store_embeddings(chunks, metadatas, collection_name="agent_learning")
        print(f"  - Learned {file_path} ({len(chunks)} chunks)")
    else:
        print(f"  - Skipped {file_path} (empty or no chunks)")


def is_valid_url(url):
    """
    Checks if a given string is a valid URL.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def learn_url(url):
    """
    Learns the content of a URL and stores its embeddings (chunked).
    """
    from utils.web_scraper import scrape_text

    if not is_valid_url(url):
        return f"Invalid URL: {url}"

    try:
        content = scrape_text(url)
        if content:
            chunks = chunk_text(content)
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadatas.append({"source": url, "chunk_index": i})

            store_embeddings(chunks, metadatas, collection_name="agent_learning")
            return f"Successfully learned content from {url} ({len(chunks)} chunks)"
        else:
            return f"Could not retrieve content from {url}"
    except Exception as e:
        return f"An error occurred while learning from URL {url}: {e}"


def learn_directory(path):
    """
    Recursively learns files in a directory and stores their embeddings in batch.
    """
    path = os.path.expanduser(path)

    if not os.path.isdir(path):
        return f"Path is not a valid directory: {path}"

    batch_texts = []
    batch_metadatas = []
    BATCH_SIZE = 100
    files_processed = 0

    for root, _, files in os.walk(path):
        # Skip ignored directories
        if any(
            f"/{ignored}/" in root.replace(path, "")
            for ignored in config.PROJECT_CONTEXT_IGNORE
        ) or any(root.endswith(ignored) for ignored in config.PROJECT_CONTEXT_IGNORE):
            continue

        for file in files:
            # Skip ignored files
            if file in config.PROJECT_CONTEXT_IGNORE:
                continue
            if file.startswith("."):  # Skip hidden files
                continue

            file_path = os.path.join(root, file)

            # Skip binary files
            if is_binary_file(file_path):
                print(f"  - Skipped binary file: {file_path}")
                continue

            try:
                with open(file_path, "r", errors="ignore") as f:
                    content = f.read()

                chunks = chunk_text(content)
                for i, chunk in enumerate(chunks):
                    batch_texts.append(chunk)
                    batch_metadatas.append({"source": file_path, "chunk_index": i})

                files_processed += 1

                # Flush batch
                if len(batch_texts) >= BATCH_SIZE:
                    store_embeddings(
                        batch_texts, batch_metadatas, collection_name="agent_learning"
                    )
                    batch_texts = []
                    batch_metadatas = []

            except Exception as e:
                print(f"  - Error reading {file_path}: {e}")

    # Flush remaining
    if batch_texts:
        store_embeddings(batch_texts, batch_metadatas, collection_name="agent_learning")

    return f"Finished learning directory: {path}. Processed {files_processed} files."
