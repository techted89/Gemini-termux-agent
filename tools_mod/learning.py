import os
import subprocess
import fnmatch
import google.genai as genai
from google.genai import types as genai_types
import config
from utils.learning import (
    learn_directory,
    learn_url,
    learn_file_content,
    is_binary_file,
)
import logging

logger = logging.getLogger(__name__)


def _get_ignored_patterns():
    """Helper to read patterns from .gitignore and config."""
    ignored = set(config.PROJECT_CONTEXT_IGNORE)
    try:
        # Find the repo root
        repo_root = (
            subprocess.check_output(["git", "rev-parse", "--show-toplevel"])
            .strip()
            .decode("utf-8")
        )
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
        files = (
            subprocess.check_output(["git", "ls-files"]).decode("utf-8").splitlines()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to os.walk if git is not available or not a git repo
        files = []
        for root, _, filenames in os.walk("."):
            for filename in filenames:
                files.append(os.path.join(root, filename))

    files_processed = 0

    for filepath in files:
        # Extra check for patterns not in .gitignore
        if any(fnmatch.fnmatch(filepath, p) for p in ignored_patterns if p != ""):
            continue

        # Check binary
        if is_binary_file(filepath):
            continue

        try:
            with open(filepath, "r", errors="ignore") as f:
                content = f.read()

            # Delegate to robust learning function (handles deletion + chunking)
            learn_file_content(filepath, content)
            files_processed += 1

        except FileNotFoundError:
            logger.error(f"File not found: {filepath}", exc_info=True)
        except PermissionError:
            logger.error(f"Permission denied for file: {filepath}", exc_info=True)
        except UnicodeDecodeError:
            logger.error(f"Unicode decode error for file: {filepath}", exc_info=True)
        except Exception as e:
            logger.exception(
                f"An unexpected error occurred while processing {filepath}: {e}"
            )

    return f"Successfully processed {files_processed} files in the 'agent_learning' collection."


def learn_directory_task(path):
    return learn_directory(path)


def learn_url_task(url, depth=0):
    # Ensure depth is an int
    try:
        depth = int(depth)
    except:
        depth = 0
    return learn_url(url, depth=depth)


def tool_definitions():
    return [
        genai_types.Tool(
            function_declarations=[
                genai_types.FunctionDeclaration(
                    name="learn_repo",
                    description="Learn the entire repository by embedding its files.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={},  # No parameters
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="learn_directory",
                    description="Learn a directory by embedding its files.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "path": genai_types.Schema(type=genai_types.Type.STRING)
                        },
                        required=["path"],
                    ),
                ),
                genai_types.FunctionDeclaration(
                    name="learn_url",
                    description="Learn a URL by embedding its content. Supports recursive crawling with depth.",
                    parameters=genai_types.Schema(
                        type=genai_types.Type.OBJECT,
                        properties={
                            "url": genai_types.Schema(type=genai_types.Type.STRING),
                            "depth": genai_types.Schema(
                                type=genai_types.Type.INTEGER,
                                description="Recursion depth (default 0)",
                            ),
                        },
                        required=["url"],
                    ),
                ),
            ]
        )
    ]
