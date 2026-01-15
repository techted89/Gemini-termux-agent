import os
import requests
from utils.database import store_embeddings, delete_by_metadata
from urllib.parse import urlparse
from utils.chunking import chunk_text
from utils.web_scraper import scrape_text, extract_links
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
    Clears existing embeddings for this file first.
    """
    # 1. Clear existing knowledge for this file
    delete_by_metadata("source", file_path)

    # 2. Chunk and Store
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


def learn_url(url, depth=0, visited=None):
    """
    Learns the content of a URL and stores its embeddings (chunked).
    Recursively follows links if depth > 0.
    """
    if visited is None:
        visited = set()

    if url in visited:
        return f"Already visited {url}"

    if not is_valid_url(url):
        return f"Invalid URL: {url}"

    visited.add(url)
    print(f"Learning URL: {url} (Depth remaining: {depth})")

    try:
        # Fetch content (we use requests here to get HTML for link extraction)
        response = requests.get(url)
        response.raise_for_status()
        html_content = response.text

        # Scrape text for embedding
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, "html.parser")
        text_content = soup.get_text()

        # 1. Clear existing knowledge for this URL
        delete_by_metadata("source", url)

        # 2. Chunk and Store
        if text_content:
            chunks = chunk_text(text_content)
            metadatas = []
            for i, chunk in enumerate(chunks):
                metadatas.append({"source": url, "chunk_index": i})

            store_embeddings(chunks, metadatas, collection_name="agent_learning")
            result_msg = (
                f"Successfully learned content from {url} ({len(chunks)} chunks)"
            )
        else:
            result_msg = f"Could not retrieve content from {url}"

        # 3. Recurse if depth > 0
        if depth > 0:
            links = extract_links(html_content, url)
            for link in links:
                # Basic domain restriction to prevent wandering too far
                # Only follow links on the same domain or subdomains?
                # For now, simplistic check: same netloc or similar
                if urlparse(link).netloc == urlparse(url).netloc:
                    learn_url(link, depth - 1, visited)

        return result_msg

    except Exception as e:
        return f"An error occurred while learning from URL {url}: {e}"


def learn_directory(path):
    """
    Recursively learns files in a directory and stores their embeddings in batch.
    """
    path = os.path.expanduser(path)

    if not os.path.isdir(path):
        return f"Path is not a valid directory: {path}"

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

                # Reuse learn_file_content to handle deletion and chunking
                learn_file_content(file_path, content)
                files_processed += 1

            except Exception as e:
                print(f"  - Error reading {file_path}: {e}")

    return f"Finished learning directory: {path}. Processed {files_processed} files."
