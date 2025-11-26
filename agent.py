from api import agentic_reason_and_act
from tools import tool_definitions, execute_tool
from db import store_conversation_turn

def handle_agent_task(models, initial_prompt, initial_context):
    """
    Manages the agent's workflow for a single, non-interactive task.
    """
    print("🤖 Agent started. Type 'exit' to quit.")
    user_id = "default_user"

    sys_prompt = f"""Your goal is to: {initial_prompt}.

You must structure your response in three parts: Thought, Plan, and Action.

**Thought:** First, analyze the user's query and the available context. Break down the problem and consider which tools might be useful. If you need to search for information, decide if you can narrow down the search using a filter.

**Plan:** Second, create a clear, step-by-step plan for how you will address the query. Your plan should be detailed enough for another agent to follow.

**Action:** Third, specify the action you will take. This must be either:
1. A single, valid tool call from the available tools.
2. The final, user-facing answer if no tool is needed.

When retrieving information, use this workflow:
1.  **Thought:** "I need to find information about X. Can I narrow down my search?"
2.  **Plan:** "1. Use `get_available_metadata_sources` to see what filters are available. 2. Use `get_relevant_context` with a `where_filter` to perform a targeted search."
3.  **Action:** `get_available_metadata_sources()`
"""
    history = [*initial_context, {"role": "user", "parts": [sys_prompt]}]

    # Agent execution loop
    for _ in range(10):  # Safety break after 10 iterations
        try:
            thought, function_call = agentic_reason_and_act(
                models["tools"], history, tools=list(tool_definitions.values())
            )
            print(f"🤔 Thought: {thought}")

            if function_call:
                history.append({"role": "model", "parts": [{"function_call": function_call}]})
                print(f"🛠️ Tool call: {function_call.name}")
                tool_result = execute_tool(function_call, models)
                history.append({"role": "function", "parts": [{"function_response": {"name": function_call.name, "response": {"result": str(tool_result)}}}]})
                print(f"✅ Result: {str(tool_result)[:200]}...")
                continue
            else:
                final_response = thought
                history.append({"role": "model", "parts": [final_response]})
                print(f"🤖: {final_response}")
                store_conversation_turn(initial_prompt, final_response, user_id)
                return  # Exit successfully

        except Exception as e:
            error_message = f"🔥 An error occurred: {e}"
            print(error_message)
            return  # Exit on error

    print("🚫 Agent reached maximum loop limit.")
