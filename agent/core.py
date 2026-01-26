import config
from utils.database import get_relevant_history, get_relevant_context, store_conversation_turn
from bin.tool_utils import execute_tool

def run_agent_step(model_wrapper, user_query, user_id, conversation_history, print_func=print):
    # 1. Restore the context retrieval (RAG)
    # This searches the 'agent_learning' collection for relevant code/docs
    context = get_relevant_context(user_query)
    
    # 2. Restore the MMR History retrieval
    # This fetches the last 10-15 relevant turns from 'agent_memory'
    history_turns = get_relevant_history(user_query, n_results=10)
    
    # 3. Restore the System Prompt Assembly
    # We must ensure the agent knows WHAT it is remembering
    # (Note: In this implementation, the history is passed to the API, context injection typically happens there or via history manipulation.
    # For now, we follow the user instruction to just focus on the return signature and execution loop.)
    
    # 4. Agent Reasoning Loop
    from api import agentic_reason_and_act

    # We pass the full history plus the new query
    thought, function_call = agentic_reason_and_act(model_wrapper, conversation_history)
    
    if function_call:
        print_func(f"🤖 Tool Call: {function_call.name}")
        # Execute the tool using execute_tool
        result = execute_tool(function_call, model_wrapper)

        # Append the result to history as a function_response to maintain context
        # Assuming conversation_history is a list of dicts (Gemini/standard format)
        if isinstance(conversation_history, list):
            # Typically: {"role": "function", "name": name, "content": result} or similar
            # For this agent's simplified flow (often mimicking user input for tool output):
            conversation_history.append({"role": "user", "parts": [f"Tool Output: {result}"]})

        return False, f"Tool Output: {result}", user_query

    else:
        # No tool call, just thought/response
        return True, thought, user_query
