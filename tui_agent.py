from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Static, RichLog
from textual.containers import Container
import google.generativeai as genai
from bin.tools import tool_definitions
import config
from agent.core import run_agent_step
from utils import database as db


class TuiAgentApp(App):
    """A Textual app for the Gemini agent."""

    CSS_PATH = "tui_agent.css"
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Container(
            RichLog(id="conversation", wrap=True),
            RichLog(id="log", wrap=True),
            Input(placeholder="Enter your prompt..."),
        )
        yield Footer()

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        self.query_one(Input).focus()

    def on_input_submitted(self, message: Input.Submitted) -> None:
        """Called when the user submits a prompt."""
        prompt = message.value
        self.query_one(Input).value = ""
        self.query_one("#conversation").write(f"🧑‍💻: {prompt}")
        self.run_agent(prompt)

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.dark = not self.dark

    def run_agent(self, prompt):
        """Runs the agent in a separate thread."""

        def agent_thread():
            # Initialize models
            genai.configure(api_key=config.API_KEY)
            models = {
                "default": genai.GenerativeModel(config.MODEL_NAME),
                "tools": genai.GenerativeModel(
                    config.MODEL_NAME,
                    safety_settings=config.SAFETY_SETTINGS,
                    tools=list(tool_definitions.values()),
                ),
            }

            # Initialize conversation history
            history = []
            if prompt:
                history.append({"role": "user", "parts": [prompt]})

            user_id = "tui_user"

            # Run agent step
            done, response, _ = run_agent_step(
                models, history, user_id, user_input=prompt, print_func=self.log
            )

            # If the agent is done, we get a direct response.
            if done:
                self.query_one("#conversation").write(f"🤖: {response}")
            else:
                # If not done, it means a tool was called. We need to continue stepping.
                while not done:
                    done, response, _ = run_agent_step(
                        models, history, user_id, print_func=self.log
                    )
                    if response:
                        self.query_one("#conversation").write(f"🤖: {response}")

        import threading

        thread = threading.Thread(target=agent_thread)
        thread.start()

    def log(self, message):
        """Logs a message to the log pane."""
        self.query_one("#log").write(message)


if __name__ == "__main__":
    app = TuiAgentApp()
    app.run()
