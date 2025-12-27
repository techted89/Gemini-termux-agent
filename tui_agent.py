import sys
import google.genai as genai
from tools_mod import tool_definitions
import config
from agent.core import run_agent_step
from utils import database as db
from dotenv import load_dotenv
from tools_mod import charm
import threading
import time
from utils.model_wrapper import GenerativeModelWrapper

def main(initial_agent_prompt=None):
    load_dotenv()

    # Initialize models
    try:
        models = {
            "default": GenerativeModelWrapper(config.MODEL_NAME),
            "tools": GenerativeModelWrapper(
                config.MODEL_NAME,
                safety_settings=config.SAFETY_SETTINGS,
                tools=list(tool_definitions.values()),
            ),
        }
    except Exception as e:
        print(f"Error initializing models: {e}")
        return

    # Use charm (gum/glow) for UI

    print(charm.glow_render("# Gemini CLI Agent (TUI)"))

    history = []
    user_id = "tui_user"

    if initial_agent_prompt:
        prompt = initial_agent_prompt
    else:
        prompt = charm.gum_input("Enter your prompt...", value="")

    while True:
        if not prompt:
            break

        print(charm.glow_render(f"**You:** {prompt}"))

        # Add to history
        history.append({"role": "user", "parts": [prompt]})

        # Run agent step
        done = False
        while not done:
            done, response, _ = run_agent_step(
                models, history, user_id, user_input=prompt if not history else None, print_func=lambda x: print(charm.glow_render(x))
            )
            if response:
                print(charm.glow_render(f"**Gemini:** {response}"))

        # Get next input
        prompt = charm.gum_input("Enter your reply (or leave empty to exit)...", value="")

if __name__ == "__main__":
    main()
