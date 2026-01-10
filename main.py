import sys
import config
from agent.main import handle_agent_task
from utils.model_wrapper import GenerativeModelWrapper
from tools_mod import tool_definitions

def main():
    # 1. Initialize the model dictionary required by the agent handler
    # Note: Our wrapper now handles 'tool_definitions' being a callable function
    models = {
        "main": GenerativeModelWrapper(
            model_name="gemini-2.0-flash-exp", 
            system_instruction="You are a capable Termux agent with RAG and system access.",
            tools=tool_definitions 
        )
    }

    # 2. Extract the prompt from command line arguments
    if "--agent" in sys.argv:
        try:
            idx = sys.argv.index("--agent")
            initial_prompt = " ".join(sys.argv[idx + 1:])
        except (IndexError, ValueError):
            initial_prompt = "help"
    else:
        initial_prompt = "help"

    # 3. Setup initial context (the short-term chat history)
    initial_context = []

    # 4. Execute the agent task with required arguments
    print(f"[*] Starting Agent with prompt: {initial_prompt}")
    handle_agent_task(models, initial_prompt, initial_context)

if __name__ == "__main__":
    main()
