import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from tools_mod.debug_test import run_tests


def find_python_files(directory):
    """Finds all Python files in a directory."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    return python_files


def run_project_tests():
    """Runs tests, lints, and formats all Python files in the project."""
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    python_files = find_python_files(project_root)
    all_results = {}
    for filepath in python_files:
        results = run_tests(filepath)
        all_results[filepath] = results
    return all_results


if __name__ == "__main__":
    all_results = run_project_tests()
    for filepath, results in all_results.items():
        print(f"--- RESULTS FOR {filepath} ---")
        for key, value in results.items():
            print(f"--- {key.upper()} ---")
            print(value)
            print("-" * (len(key) + 8))
        print("-" * (len(filepath) + 20))
