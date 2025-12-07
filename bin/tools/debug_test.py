import google.generativeai as genai
import subprocess
import sys


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


tool_definitions = {
    "run_tests": genai.types.Tool(
        function_declarations=[
            genai.types.FunctionDeclaration(
                name="run_tests",
                description="Runs tests, lints, and formats a Python file.",
                parameters={
                    "type": "object",
                    "properties": {"filepath": {"type": "string"}},
                    "required": ["filepath"],
                },
            )
        ]
    )
}
