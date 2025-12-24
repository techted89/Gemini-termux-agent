import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools_mod.debug_test import run_tests

if __name__ == "__main__":
    results = run_tests("tests/agent_verify_prompt.py")
    for key, value in results.items():
        print(f"--- {key.upper()} ---")
        print(value)
        print("-" * (len(key) + 8))
