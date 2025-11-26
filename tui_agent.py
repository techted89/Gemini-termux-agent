from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import google.generativeai as genai
import config
from tools import tool_definitions
from agent import run_agent_step

def tui_print_func(output):
    """
    Custom print function for the TUI to format agent output.
    """
    console = Console()
    if "🤔 Thought:" in output:
        # Style thoughts differently to distinguish them
        console.print(Panel(f"[yellow]{output}[/yellow]", title="Thought", border_style="yellow"))
    else:
        # All other outputs are treated as standard messages
        console.print(output)

def main(initial_agent_prompt=None):
    console = Console()
    session = PromptSession()
    genai.configure(api_key=config.API_KEY)

    models = {
        "default": genai.GenerativeModel(config.MODEL_NAME),
        "tools": genai.GenerativeModel(
            config.MODEL_NAME,
            safety_settings=config.SAFETY_SETTINGS,
            tools=list(tool_definitions.values()),
        ),
    }

    console.print(Panel("[bold green]Gemini TUI Agent[/bold green]", expand=False))

    user_id = "default_user"  # In a real app, this would be dynamic
    history = [{"role": "user", "parts": ["You are a helpful AI assistant operating in a Termux environment."]}]

    if initial_agent_prompt:
        history.append({"role": "user", "parts": [initial_agent_prompt]})
        # Initial run to kick-start the agent
        done, response = run_agent_step(models, history, print_func=tui_print_func)
        if response:
            console.print(Markdown(response))
    else:
        done = True

    while True:
        try:
            if done:
                user_input = session.prompt(HTML("<ansigreen><b>You: </b></ansigreen>"))
                if user_input.lower() in ["exit", "quit"]:
                    break
                if not user_input.strip():
                    continue
                # The user's input kicks off a new agent turn
                done, response, _ = run_agent_step(models, history, user_id, user_input=user_input, print_func=tui_print_func)
            else:
                # Continue the agent's turn until it's done
                done, response, _ = run_agent_step(models, history, user_id, print_func=tui_print_func)

            if response:
                console.print(Markdown(response))

        except KeyboardInterrupt:
            break
        except Exception as e:
            console.print(f"[bold red]An error occurred: {e}[/bold red]")
            break

if __name__ == "__main__":
    main()
