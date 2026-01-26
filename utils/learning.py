import os
from utils.database import store_embedding
from urllib.parse import urlparse
import config

def learn_file_content(file_path, content):
    """
    Learns the content of a single file and stores its embedding.
    """
    store_embedding(content, {"source": file_path}, collection_name="agent_learning")
    print(f"  - Learned {file_path}")

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
    Learns the content of a URL and stores its embeddings.
    """
    from utils.web_scraper import scrape_text

    if not is_valid_url(url):
        return f"Invalid URL: {url}"

    try:
        content = scrape_text(url)
        if content:
            # We could chunk this for larger pages
            store_embedding(content, {"source": url}, collection_name="agent_learning")
            return f"Successfully learned content from {url}"
        else:
            return f"Could not retrieve content from {url}"
    except Exception as e:
        return f"An error occurred while learning from URL {url}: {e}"


def learn_directory(path):
    """
    Recursively learns files in a directory and stores their embeddings.
    """
    path = os.path.expanduser(path)

    if not os.path.isdir(path):
        return f"Path is not a valid directory: {path}"

    for root, _, files in os.walk(path):
        # Skip ignored directories
        if any(f"/{ignored}/" in root.replace(path, "") for ignored in config.PROJECT_CONTEXT_IGNORE) or any(root.endswith(ignored) for ignored in config.PROJECT_CONTEXT_IGNORE):
            continue

        for file in files:
            # Skip ignored files
            if file in config.PROJECT_CONTEXT_IGNORE:
                continue

            file_path = os.path.join(root, file)
            try:
                with open(file_path, "r", errors="ignore") as f:
                    content = f.read()
                learn_file_content(file_path, content)
            except Exception as e:
                print(f"  - Error reading {file_path}: {e}")

    return f"Finished learning directory: {path}"
