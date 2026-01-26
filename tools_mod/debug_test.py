import google.genai as genai
import subprocess
import sys
import time

def run_tests(filepath):
    """
    Runs tests, lints, and formats a Python file.
    """
    results = {}

    # Run tests
    try:
        test_result = subprocess.run(
            [sys.executable, "-m", "unittest", filepath],
            capture_output=True,
            text=True,
            check=True,
        )
        results["tests"] = test_result.stderr
    except subprocess.CalledProcessError as e:
        results["tests"] = e.stderr

    # Run linter
    try:
        lint_result = subprocess.run(
            [sys.executable, "-m", "flake8", filepath],
            capture_output=True,
            text=True,
            check=True,
        )
        results["linting"] = lint_result.stdout or "No linting issues found."
    except subprocess.CalledProcessError as e:
        results["linting"] = e.stdout

    # Run formatter
    try:
        format_result = subprocess.run(
            [sys.executable, "-m", "black", filepath],
            capture_output=True,
            text=True,
            check=True,
        )
        results["formatting"] = format_result.stderr or "No formatting changes needed."
    except subprocess.CalledProcessError as e:
        results["formatting"] = e.stderr

    return results

def debug_failure_task(error_type):
    """
    Intentionally raises an error to test the agent's error handling.
    Supported types: 'ValueError', 'ZeroDivisionError', 'Timeout', 'RuntimeError'
    """
    if error_type == "ValueError":
        raise ValueError("This is a debug ValueError.")
    elif error_type == "ZeroDivisionError":
        return 1 / 0
    elif error_type == "Timeout":
        time.sleep(60) # Simulate timeout (may not actually trigger agent timeout immediately)
        return "Finished wait (did not timeout system-level)."
    elif error_type == "RuntimeError":
        raise RuntimeError("This is a debug RuntimeError.")
    else:
        return f"Unknown error type: {error_type}"

def debug_echo_task(content):
    """Echoes content back. Useful for verifying tool connectivity."""
    return f"Debug Echo: {content}"

def tool_definitions():
    return [
        genai.types.Tool(
            function_declarations=[
                genai.types.FunctionDeclaration(
                    name="run_tests",
                    description="Runs tests, lints, and formats a Python file.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "filepath": {
                                "type": "string",
                                "description": "Path to the Python file to test, lint, and format"
                            }
                        },
                        "required": ["filepath"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="debug_failure",
                    description="Intentionally raises an error for debugging purposes.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "error_type": {
                                "type": "string",
                                "description": "Type of error to raise (ValueError, ZeroDivisionError, Timeout, RuntimeError)"
                            }
                        },
                        "required": ["error_type"],
                    },
                ),
                genai.types.FunctionDeclaration(
                    name="debug_echo",
                    description="Echoes the input content back.",
                    parameters={
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"}
                        },
                        "required": ["content"],
                    },
                ),
            ]
        )
    ]

library = {
    "run_tests": run_tests,
    "debug_failure": debug_failure_task,
    "debug_echo": debug_echo_task,
}
