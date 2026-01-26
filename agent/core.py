import config
from utils.database import get_relevant_history, get_relevant_context
from tools_mod import execute_tool
from api import agentic_reason_and_act

def run_agent_step(models, conversation_history, user_id, user_input=None, print_func=print):
    """
    Executes a single step of the agent loop.
    
    Args:
        models (dict): Dictionary of model wrappers.
        conversation_history (list): List of conversation turns.
        user_id (str): The user ID.
        user_input (str, optional): The new user input, if any.
        print_func (callable): Function to use for printing.
    
    Returns:
        tuple: (done (bool), response (str), last_user_input (str))
    """
    model_wrapper = models["main"]
    
    # 1. Handle User Input
    if user_input:
        conversation_history.append({"role": "user", "parts": [user_input]})
        user_query = user_input
    else:
        # Determine query from history (likely the last user message text)
        user_query = ""
        for turn in reversed(conversation_history):
            if turn.get("role") == "user":
                for part in turn.get("parts", []):
                    if isinstance(part, str):
                        user_query = part
                        break
            if user_query:
                break
    
    # 2. Context Retrieval (RAG)
    # Note: Currently we just fetch it but don't inject it yet as the injection mechanism was incomplete.
    # Future improvement: Inject context into system instructions or ephemeral history messages.
    if user_query:
        context = get_relevant_context(user_query)
        history_turns = get_relevant_history(user_query, n_results=10)

    # 3. Call API
    # agentic_reason_and_act returns (thought, function_call)
    thought, function_call = agentic_reason_and_act(model_wrapper, conversation_history)

    # 4. Handle Tool Execution
    if function_call:
        tool_name = function_call.name
        tool_args = function_call.args

        print_func(f"🛠️ Executing tool: {tool_name} with args: {tool_args}")

        # Convert args to dict if needed (sdk returns Map)
        if hasattr(tool_args, "items"):
            args_dict = dict(tool_args.items())
        else:
            args_dict = tool_args

        tool_result = execute_tool(tool_name, args_dict)

        # Append result to history
        conversation_history.append({
            "role": "user",
            "parts": [{
                "function_response": {
                    "name": tool_name,
                    "response": {"result": tool_result}
                }
            }]
        })

        # done=False means continue the loop (agent will see result and react)
        return False, thought, user_query

    # 5. Handle Final Response
    if thought:
        conversation_history.append({"role": "model", "parts": [thought]})
    return True, thought, user_query
