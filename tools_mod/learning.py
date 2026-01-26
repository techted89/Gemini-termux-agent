import os
import subprocess
import fnmatch
from google.genai import types as genai_types
from utils.database import store_embedding, store_embeddings
import config
from utils.learning import learn_directory, learn_url
import logging

logger = logging.getLogger(__name__)

def _get_ignored_patterns():
    """Helper to read patterns from .gitignore and config."""
    ignored = set(config.PROJECT_CONTEXT_IGNORE)
    try:
        # Find the repo root
        repo_root = subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).strip().decode('utf-8')
        gitignore_path = os.path.join(repo_root, ".gitignore")
        with open(gitignore_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored.add(line)
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Error getting .gitignore: {e}", exc_info=True)
        pass  # No .gitignore or not a git repo, no problem
    return ignored

def learn_repo_task():
    """
    Reads all files in the repository, respects .gitignore and PROJECT_CONTEXT_IGNORE,
    and stores their content as embeddings in ChromaDB.
    """
    ignored_patterns = _get_ignored_patterns()

    # Use git to list all files, which respects .gitignore
    try:
        files = subprocess.check_output(["git", "ls-files"]).decode("utf-8").splitlines()
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to os.walk if git is not available or not a git repo
        files = []
        for root, _, filenames in os.walk("."):
            for filename in filenames:
                files.append(os.path.join(root, filename))

    stored_count = 0
    batch_texts = []
    batch_metadatas = []
    batch_size = 50

    def process_batch():
        nonlocal batch_texts, batch_metadatas, stored_count
        if not batch_texts:
            return

        if store_embeddings(batch_texts, batch_metadatas):
             stored_count += len(batch_texts)
        else:
             # Fallback
             for t, m in zip(batch_texts, batch_metadatas):
                 try:
                     store_embedding(t, m)
                     stored_count += 1
                 except Exception:
                     pass

        batch_texts[:] = []
        batch_metadatas[:] = []

    for filepath in files:
        # Extra check for patterns not in .gitignore
        if any(fnmatch.fnmatch(filepath, p) for p in ignored_patterns if p != ""):
            continue

        try:
            with open(filepath, "r", errors="ignore") as f:
                content = f.read()

            # We use the filepath as 'source' metadata
            metadata = {"source": filepath}

            batch_texts.append(content)
            batch_metadatas.append(metadata)

            if len(batch_texts) >= batch_size:
                process_batch()

        except FileNotFoundError:
            logger.error(f"File not found: {filepath}", exc_info=True)
        except PermissionError:
            logger.error(f"Permission denied for file: {filepath}", exc_info=True)
        except UnicodeDecodeError:
            logger.error(f"Unicode decode error for file: {filepath}", exc_info=True)
        except Exception as e:
            logger.exception(f"An unexpected error occurred while processing {filepath}: {e}")

    process_batch()

    return f"Successfully stored content from {stored_count} files in the 'agent_learning' collection."

def learn_directory_task(path):
    return learn_directory(path)

def learn_url_task(url):
    return learn_url(url)

def tool_definitions():
    return [
        genai_types.Tool(
            function_declarations=[
                genai_types.FunctionDeclaration(
                    name="learn_repo",
                    description="Learn the entire repository by embedding its files.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={}, # No parameters
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="learn_directory",
                    description="Learn a directory by embedding its files.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={"path": genai_types.Schema(type=genai_types.Type.STRING)},
                        required=["path"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="learn_url",
                    description="Learn a URL by embedding its content.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={"url": genai_types.Schema(type=genai_types.Type.STRING)},
                        required=["url"],
                    ),
                ),
            ]
        )
    ]
