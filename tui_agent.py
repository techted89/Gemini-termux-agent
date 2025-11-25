from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
import google.generativeai as genai
import config
from tools import tool_definitions
from agent import run_agent_step


def main(initial_agent_prompt=None):
    console = Console()
    session = PromptSession()
    genai.configure(api_key=config.API_KEY)
    models = {
        "default": genai.GenerativeModel(
            config.MODEL_NAME, safety_settings=config.SAFETY_SETTINGS
        ),
        "tools": genai.GenerativeModel(
            config.MODEL_NAME,
            safety_settings=config.SAFETY_SETTINGS,
            tools=list(tool_definitions.values()),
        ),
    }
    console.print(Panel("[bold green]Gemini TUI (Sync)[/bold green]", expand=False))
    history = [{"role": "user", "parts": ["You are a Termux AI Agent."]}]

    if initial_agent_prompt:
        history.append({"role": "user", "parts": [initial_agent_prompt]})
        is_done = False
        while not is_done:
            is_done, res, _ = run_agent_step(models, history, print_func=console.print)
            if res:
                console.print(Markdown(res))

    while True:
        try:
            u = session.prompt(HTML("<ansigreen><b>Gemini> </b></ansigreen>"))
            if u.lower() in ["exit", "quit"]:
                break
            if not u.strip():
                continue

            is_done, res, _ = run_agent_step(
                models, history, user_input=u, print_func=console.print
            )
            if res:
                console.print(Markdown(res))
            while not is_done:
                is_done, res, _ = run_agent_step(
                    models, history, user_input=None, print_func=console.print
                )
                if res:
                    console.print(Markdown(res))
        except:
            break


if __name__ == "__main__":
    main()
