import sys
import os

# Add the parent directory of gemini_cli to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from api import agentic_plan, agentic_reason, agentic_execute
from tools import tool_definitions  # Assuming tool_definitions is available


def test_agentic_functions():
    print("Testing Agentic Plan...")
    plan_prompt = "Develop a simple Python script to list files in a directory."
    plan_output = agentic_plan(prompt=plan_prompt, tools=tool_definitions)
    print(plan_output)
    assert "Agentic Plan:" in plan_output
    assert "Understand the goal" in plan_output
    assert (
        "Gather initial information using google_search" in plan_output
    )  # Should include search if available

    # NEW TEST CASE 1: Test agentic_plan with a prompt explicitly suggesting tool usage
    print("\nTesting Agentic Plan with explicit tool suggestion...")
    plan_prompt_with_tool = "Develop a web scraper using the web_interact_task tool."
    plan_output_with_tool = agentic_plan(
        prompt=plan_prompt_with_tool, tools=tool_definitions
    )
    print(plan_output_with_tool)
    assert "Agentic Plan:" in plan_output_with_tool
    assert "Understand the goal" in plan_output_with_tool
    # Assert that the suggested tool is mentioned in the plan's output.
    assert "web_interact_task" in plan_output_with_tool
    print("Agentic Plan with explicit tool suggestion tested successfully.")

    print("\nTesting Agentic Reason...")
    reason_output = agentic_reason(plan=plan_output, tools=tool_definitions)
    print(reason_output)
    assert (
        "[SIMULATED RESPONSE for: Given the plan:" in reason_output
    )  # Check for simulated response
    assert "elaborate on it by breaking it down" in reason_output

    # NEW TEST CASE 2: Test agentic_reason with a more elaborate plan
    print("\nTesting Agentic Reason with a more elaborate plan...")
    more_elaborate_plan = """Agentic Plan:
    1. Understand the goal: Create a simple "Hello World" web server in Python.
    2. Break down the task:
        - Identify necessary Python modules (e.g., http.server).
        - Write server code (create file).
        - Run the server (execute shell command).
    3. Determine tools needed:
        - google_search: To find examples/documentation for Python web servers.
        - create file: To write the Python script.
        - execute shell command: To run the Python script.
    """
    reason_output_elaborate = agentic_reason(
        plan=more_elaborate_plan, tools=tool_definitions
    )
    print(reason_output_elaborate)
    assert "[SIMULATED RESPONSE for: Given the plan:" in reason_output_elaborate
    assert "elaborate on it by breaking it down" in reason_output_elaborate
    print("Agentic Reason with elaborate plan tested successfully.")

    print("\nTesting Agentic Execute (Google Search)...")
    execute_search_action = "google search for 'python list files in directory'"
    execute_search_output = agentic_execute(
        action=execute_search_action, tools=tool_definitions
    )
    print(execute_search_output)
    assert (
        "[SIMULATED RESPONSE for: The agent is executing the following action: 'google search for 'python list files in directory''."
        in execute_search_output
    )
    assert (
        "- Initiated a Google search for: 'python list files in directory'."
        in execute_search_output
    )

    print("\nTesting Agentic Execute (Read File)...")
    execute_read_action = "read file '~/gemini_cli/api.py'"
    execute_read_output = agentic_execute(
        action=execute_read_action, tools=tool_definitions
    )
    print(execute_read_output)
    assert (
        "[SIMULATED RESPONSE for: The agent is executing the following action: 'read file '~/gemini_cli/api.py''."
        in execute_read_output
    )
    assert "- Attempted to read file: '~/gemini_cli/api.py'." in execute_read_output

    print("\nTesting Agentic Execute (Shell Command)...")
    execute_shell_action = "execute shell command 'ls -la'"
    execute_shell_output = agentic_execute(
        action=execute_shell_action, tools=tool_definitions
    )
    print(execute_shell_output)
    assert (
        "[SIMULATED RESPONSE for: The agent is executing the following action: 'execute shell command 'ls -la''."
        in execute_shell_output
    )
    assert "- Executed shell command: 'ls -la'." in execute_shell_output

    # NEW TEST CASE 3.1: Test agentic_execute with 'create file' action
    print("\nTesting Agentic Execute (Create File)...")
    execute_create_action = (
        "create file 'new_script.py' with content 'print(\"Hello World\")'"
    )
    execute_create_output = agentic_execute(
        action=execute_create_action, tools=tool_definitions
    )
    print(execute_create_output)
    assert (
        f"[SIMULATED RESPONSE for: The agent is executing the following action: '{execute_create_action}'."
        in execute_create_output
    )
    assert "- Created file: 'new_script.py'." in execute_create_output
    print("Agentic Execute (Create File) tested successfully.")

    # NEW TEST CASE 3.2: Test agentic_execute with 'edit file' action
    print("\nTesting Agentic Execute (Edit File)...")
    execute_edit_action = (
        "edit file 'existing_file.txt' by replacing 'old_text' with 'new_text'"
    )
    execute_edit_output = agentic_execute(
        action=execute_edit_action, tools=tool_definitions
    )
    print(execute_edit_output)
    assert (
        f"[SIMULATED RESPONSE for: The agent is executing the following action: '{execute_edit_action}'."
        in execute_edit_output
    )
    assert "- Edited file: 'existing_file.txt'." in execute_edit_output
    print("Agentic Execute (Edit File) tested successfully.")

    print("\nAll agentic functions tested successfully.")


if __name__ == "__main__":
    test_agentic_functions()
