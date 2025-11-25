from api import call_gemini_api
from tools import tool_definitions, execute_tool
from db import get_relevant_context # Import the function

def run_agent_step(
    models, history, user_input=None, print_func=print, verbose_mode=False
):
    """
    Executes a single step of the agent's turn.
    Returns (done, result_text, metadata).
    - done: True if the agent has finished processing (either responded with text or error), False if it made a tool call and needs to process the result.
    - result_text: The text output to be displayed to the user.
    - metadata: (Currently None, but can be used for more complex state/data in the future).
    """
    if user_input:
        # Retrieve relevant context from ChromaDB
        relevant_context = get_relevant_context(user_input)
        
        # Prepend the context to the user input
        if relevant_context:
            user_input = f"{relevant_context}\n{user_input}"
        
        history.append({"role": "user", "parts": [user_input]})

    try:
        response = call_gemini_api(
            models["tools"], history, tools=list(tool_definitions.values())
        )

        function_call, text_content = None, ""
        if response.parts:
            for part in response.parts:
                if hasattr(part, "function_call") and part.function_call:
                    function_call = part.function_call
                text_val = getattr(part, "text", None)
                if text_val:
                    text_content += text_val

        if function_call:
            # Add model's thought/call to history
            history.append({"role": "model", "parts": response.parts})

            if text_content and verbose_mode:
                print_func(f"🤖 {text_content}")

            # Execute tool
            print_func(f"⚙️ Tool: {function_call.name}")
            # Note: The `execute_tool` function might need the `models` dictionary
            # if tools themselves require access to different model configurations.
            tool_result = execute_tool(function_call, models)  # SYNC CALL

            # Add result to history
            history.append(
                {
                    "role": "function",
                    "parts": [
                        {
                            "function_response": {
                                "name": function_call.name,
                                "response": {"result": str(tool_result)},
                            }
                        }
                    ],
                }
            )
            print_func(
                f"✅ Result: {str(tool_result)[:100]}..."
            )  # Truncate for display
            return False, None, None  # Not done, as it needs to process the tool result

        elif text_content:
            history.append({"role": "model", "parts": [text_content]})
            return True, text_content, None  # Done, responded with text

        return (
            True,
            "⚠️ Agent returned empty response.",
            None,
        )  # Done, but with an empty response

    except Exception as e:
        return True, f"🔥 Error: {e}", None  # Done, due to an error


def handle_agent_task(models, initial_prompt, initial_context):
    """
    Handles a full agent task in a CLI loop.
    This replaces the previous handle_agent_task and process_agent_turn functions.
    """
    print("🤖 Agent mode. Type 'exit' to quit.")

    # Initialize history with the system prompt
    sys_prompt = f"You are a Termux AI Agent. Goal: {initial_prompt}"
    hist = [*initial_context, {"role": "user", "parts": [sys_prompt]}]

    # Initial kick-off for the agent to start working on the goal
    done = False
    while not done:
        done, res, _ = run_agent_step(models, hist)
        if res:
            print(f"🤖 {res}")

    # Main loop for user interaction and continued agent processing
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            # Process user input
            done, res, _ = run_agent_step(models, hist, user_input=user_input)
            if res:
                print(f"🤖 {res}")

            # Continue agent processing until it's "done" (either responded or errored)
            while not done:
                done, res, _ = run_agent_step(models, hist)
                if res:
                    print(f"🤖 {res}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"🔥 An error occurred during user interaction: {e}")
            break
