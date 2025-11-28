from dotenv import load_dotenv
load_dotenv()
from tools_mod import charm
import google.generativeai as genai
import config
from tools_mod import tool_definitions
from agent import run_agent_step
import sys

def tui_print_func(output):
    """
    Custom print function using Charm tools.
    """
    if "🤔 Thought:" in output:
        # Style thoughts
        charm.gum_style(output, foreground="220", border="rounded", border_foreground="220")
    elif "🛠️ Tool call:" in output:
        charm.gum_style(output, foreground="212", border="normal", border_foreground="212")
    else:
        print(output)

def main(initial_agent_prompt=None):
    genai.configure(api_key=config.API_KEY)

    models = {
        "default": genai.GenerativeModel(config.MODEL_NAME),
        "tools": genai.GenerativeModel(
            config.MODEL_NAME,
            safety_settings=config.SAFETY_SETTINGS,
            tools=list(tool_definitions.values()),
        ),
    }

    charm.gum_style("Gemini TUI Agent", foreground="46", border="double", padding="1 4", border_foreground="46")

    user_id = "default_user"
    history = [{"role": "user", "parts": ["You are a helpful AI assistant operating in a Termux environment."]}]

    if initial_agent_prompt:
        history.append({"role": "user", "parts": [initial_agent_prompt]})
        print("🤖 Processing initial prompt...")
        done, response, _ = run_agent_step(models, history, user_id, print_func=tui_print_func)
        if response:
            charm.glow_print(response)
    else:
        done = True

    while True:
        try:
            if done:
                # Use gum input
                user_input = charm.gum_input(placeholder="Ask me something...", prompt="You: ")

                # Check for empty input (gum might return empty on cancel/EOF?)
                if user_input == "" and not sys.stdin.isatty():
                     # Prevent infinite loop if non-interactive
                     break

                if user_input.strip() == "":
                    continue

                if user_input.lower() in ["exit", "quit"]:
                    break

                if user_input.startswith("/plan ") or user_input.startswith("/agent "):
                    cmd_len = 6 if user_input.startswith("/plan ") else 7
                    prompt = user_input[cmd_len:].strip()
                    user_input = f"Using the `agentic_plan` tool, create a detailed plan for: {prompt}"
                    charm.gum_style(f"Agent Mode: {prompt}", foreground="33", border="normal", border_foreground="33")

                done, response, _ = run_agent_step(models, history, user_id, user_input=user_input, print_func=tui_print_func)
            else:
                done, response, _ = run_agent_step(models, history, user_id, print_func=tui_print_func)

            if response:
                charm.glow_print(response)

        except KeyboardInterrupt:
            break
        except Exception as e:
            charm.gum_style(f"An error occurred: {e}", foreground="196", border="thick", border_foreground="196")
            break

if __name__ == "__main__":
    main()
