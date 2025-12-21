from api import agentic_reason_and_act, call_gemini_api
from tools_mod import tool_definitions
from bin.tool_utils import execute_tool
from utils.database import (
    get_relevant_context,
    store_conversation_turn,
    get_relevant_history,
)
from tools_mod.nlp import huggingface_sentence_similarity


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

        standalone_question = call_gemini_api(
            models["default"], [{"role": "user", "parts": [contextualize_prompt]}]
        ).text.strip()
        print_func(f"🔎 Standalone Question: {standalone_question}")

        # 2. Retrieve relevant history
        history_context = get_relevant_history(standalone_question, user_id)

        # 3. Retrieve relevant context
        context = get_relevant_context(standalone_question)

        # 4. Hugging Face sentence similarity
        if context:
            similarity_scores = huggingface_sentence_similarity(
                standalone_question, context
            )
            # 5. Construct the final prompt
            final_input = f"{history_context}\n{similarity_scores}\nUser query: {standalone_question}"
        else:
            final_input = f"{history_context}\nUser query: {standalone_question}"

        history.append({"role": "user", "parts": [final_input]})

    try:
        thought, function_call = agentic_reason_and_act(
            models["tools"], history, tools=list(tool_definitions.values())
        )
        print_func(f"🤔 Thought: {thought}")

        if function_call:
            history.append(
                {"role": "model", "parts": [{"function_call": function_call}]}
            )
            print_func(f"🛠️ Tool call: {function_call.name}")
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
