import os
import subprocess
import google.genai as genai
from google.genai import types as genai_types
from utils.database import store_embedding
import config

def _get_ignored_patterns():
    """Helper to read patterns from .gitignore and config."""
    ignored = set(config.PROJECT_CONTEXT_IGNORE)
    try:
        with open(".gitignore", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    ignored.add(line)
    except FileNotFoundError:
        pass  # No .gitignore, no problem
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
    for filepath in files:
        # Extra check for patterns not in .gitignore
        if any(p in filepath for p in ignored_patterns if p != ""):
            continue

        try:
            with open(filepath, "r", errors="ignore") as f:
                content = f.read()

            # We use the filepath as 'source' metadata
            metadata = {"source": filepath}
            store_embedding(content, metadata, collection_name="agent_learning")
            stored_count += 1
        except Exception as e:
            print(f"Could not process {filepath}: {e}")

    return f"Successfully stored content from {stored_count} files in the 'agent_learning' collection."

from utils.learning import learn_directory, learn_url

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
