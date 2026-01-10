import config
from utils.database import get_relevant_history, get_relevant_context
from tools_mod import execute_tool

def run_agent_step(model_wrapper, user_query, user_id, conversation_history, print_func=print):
    # 1. Restore the context retrieval (RAG)
    # This searches the 'agent_learning' collection for relevant code/docs
    context = get_relevant_context(user_query)
    
    # 2. Restore the MMR History retrieval
    # This fetches the last 10-15 relevant turns from 'agent_memory'
    history_turns = get_relevant_history(user_query, n_results=10)
    
    # 3. Restore the System Prompt Assembly
    # We must ensure the agent knows WHAT it is remembering
    system_prompt_extension = f"\nRelevant Context:\n{context}\n\nRelevant Past Conversations:\n{history_turns}"
    
    # 4. Agent Reasoning Loop
    from api import agentic_reason_and_act
    # We pass the full history plus the new query
    thought, function_call = agentic_reason_and_act(model_wrapper, conversation_history)
    
    return thought, function_call