from api import agentic_reason_and_act, call_gemini_api
from tools import tool_definitions, execute_tool
from db import get_relevant_context, get_available_metadata_sources, store_conversation_turn, get_relevant_history

def run_agent_step(models, history, user_id, user_input=None, print_func=print):
    """
    Executes one step of the agent's reasoning loop.
    """
    if user_input:
        # 1. Contextualize the user's query
        contextualize_prompt = f"""Based on the last few turns of the conversation, rewrite the user's latest query: '{user_input}'
                                 into a standalone question.

                                 CONVERSATION HISTORY:
                                 {''.join([f'{turn["role"]}: {turn["parts"][0]}\n' for turn in history[-3:]])}

                                 STANDALONE QUESTION:"""
        
        standalone_question = call_gemini_api(models["default"], [{"role": "user", "parts": [contextualize_prompt]}]).text.strip()
        print_func(f"🔎 Standalone Question: {standalone_question}")

        # 2. Retrieve relevant history
        history_context = get_relevant_history(standalone_question, user_id)
        
        # 3. Inject context and append to history
        final_input = f"{history_context}\nUser query: {standalone_question}"
        history.append({"role": "user", "parts": [final_input]})

    try:
        thought, function_call = agentic_reason_and_act(
            models["tools"], history, tools=list(tool_definitions.values())
        )
        print_func(f"🤔 Thought: {thought}")

        if function_call:
            history.append({"role": "model", "parts": [{"function_call": function_call}]})
            print_func(f"🛠️ Tool call: {function_call.name}")
            tool_result = execute_tool(function_call, models)
            history.append({"role": "function", "parts": [{"function_response": {"name": function_call.name, "response": {"result": str(tool_result)}}}]})
            print_func(f"✅ Result: {str(tool_result)[:200]}...")
            return False, None, user_input  # Return the original user_input
        else:
            final_response = thought
            history.append({"role": "model", "parts": [final_response]})
            # Store the conversation turn
            if user_input:
                store_conversation_turn(user_input, final_response, user_id)
            return True, final_response, None

    except Exception as e:
        error_message = f"🔥 An error occurred: {e}"
        print_func(error_message)
        return True, error_message, None

def handle_agent_task(models, initial_prompt, initial_context):
    """
    Manages the agent's workflow for a given task.
    """
    print("🤖 Agent started. Type 'exit' to quit.")
    user_id = "default_user"  # In a real app, this would be dynamic

    sys_prompt = f"""Your goal is to: {initial_prompt}.
    When you need to retrieve information, first consider if you can narrow down your search.
    Use the `get_available_metadata_sources` tool to see what sources you can filter by.
    Then, use the `get_relevant_context` tool with a `where_filter` to perform a targeted search.
    """
    history = [*initial_context, {"role": "user", "parts": [sys_prompt]}]

    done, response, last_user_input = run_agent_step(models, history, user_id, print_func=print)
    if response:
        print(f"🤖: {response}")

    while True:
        try:
            if done:
                user_input = input("🧑‍💻 You: ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                done, response, last_user_input = run_agent_step(models, history, user_id, user_input=user_input, print_func=print)
            else:
                done, response, _ = run_agent_step(models, history, user_id, print_func=print)

            if response:
                print(f"🤖: {response}")
                # If a final response was given after a tool call, store the turn
                if last_user_input:
                    store_conversation_turn(last_user_input, response, user_id)

        except KeyboardInterrupt:
            print("\n👋 Agent stopped by user.")
            break
        except Exception as e:
            print(f"🔥 A critical error occurred: {e}")
            break
