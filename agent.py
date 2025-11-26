from api import agentic_reason_and_act
from tools import tool_definitions, execute_tool
from db import get_relevant_context, get_available_metadata_sources

def run_agent_step(models, history, user_input=None, print_func=print):
    """
    Executes one step of the agent's reasoning loop.
    """
    if user_input:
        # 1. Append user input to history. The context retrieval is now part of the agent's
        #    reasoning process, so we no longer pre-fetch it here.
        history.append({"role": "user", "parts": [user_input]})

    try:
        # 2. Get the agent's thought and next action
        #    The `agentic_reason_and_act` function is where the agent decides
        #    whether to call a tool (like `get_relevant_context` with a filter)
        #    or to respond directly.
        thought, function_call = agentic_reason_and_act(
            models["tools"], history, tools=list(tool_definitions.values())
        )

        # Print the agent's thought process
        print_func(f"🤔 Thought: {thought}")

        if function_call:
            # 3. If a tool is called, execute it
            history.append(
                {
                    "role": "model",
                    "parts": [{"function_call": function_call}],
                }
            )
            print_func(f"🛠️ Tool call: {function_call.name}")

            # The agent is now responsible for calling `get_relevant_context`
            # with or without a `where_filter` as part of its tool execution.
            tool_result = execute_tool(function_call, models)

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
            print_func(f"✅ Result: {str(tool_result)[:200]}...")
            return False, None  # The agent's turn is not done yet

        else:
            # 4. If no tool is called, it's a final response
            final_response = thought
            history.append({"role": "model", "parts": [final_response]})
            return True, final_response  # The agent's turn is done

    except Exception as e:
        # 5. Handle any errors that occur
        error_message = f"🔥 An error occurred: {e}"
        print_func(error_message)
        return True, error_message  # End the turn on error

def handle_agent_task(models, initial_prompt, initial_context):
    """
    Manages the agent's workflow for a given task.
    """
    print("🤖 Agent started. Type 'exit' to quit.")

    # 1. Initialize conversation history with a more detailed system prompt
    #    that encourages the use of filtering.
    sys_prompt = f"""Your goal is to: {initial_prompt}.

    When you need to retrieve information, first consider if you can narrow down your search.
    Use the `get_available_metadata_sources` tool to see what sources you can filter by.
    Then, use the `get_relevant_context` tool with a `where_filter` to perform a targeted search.
    """
    history = [*initial_context, {"role": "user", "parts": [sys_prompt]}]

    # 2. Kick-off the agent's first step
    done, response = run_agent_step(models, history, print_func=print)
    if response:
        print(f"🤖: {response}")

    # 3. Main loop for the agent's execution
    while True:
        try:
            # Check if the last step was final
            if done:
                user_input = input("🧑‍💻 You: ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                done, response = run_agent_step(models, history, user_input=user_input, print_func=print)
            else:
                # If the agent's turn is not done, continue the loop
                done, response = run_agent_step(models, history, print_func=print)

            if response:
                print(f"🤖: {response}")

        except KeyboardInterrupt:
            print("\n👋 Agent stopped by user.")
            break
        except Exception as e:
            print(f"🔥 A critical error occurred: {e}")
            break
