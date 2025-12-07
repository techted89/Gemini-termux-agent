from agent.core import run_agent_step
from utils.database import store_conversation_turn


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

    done, response, last_user_input = run_agent_step(
        models, history, user_id, print_func=print
    )
    if response:
        print(f"🤖: {response}")

    while True:
        try:
            if done:
                user_input = input("🧑‍💻 You: ")
                if user_input.lower() in ["exit", "quit"]:
                    break
                done, response, last_user_input = run_agent_step(
                    models, history, user_id, user_input=user_input, print_func=print
                )
            else:
                done, response, _ = run_agent_step(
                    models, history, user_id, print_func=print
                )

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
