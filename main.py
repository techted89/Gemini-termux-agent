import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai
import config
import tasks
from utils import database as db
from agent.main import handle_agent_task
from tools_mod import tool_definitions
import tui_agent


def main():
    parser = argparse.ArgumentParser(
        description="A CLI tool to interact with Google Gemini, with agentic capabilities."
    )

    # Modes of Operation
    parser.add_argument(
        "--tui", action="store_true", help="Run the agent in interactive Text UI mode."
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="Run in autonomous agent mode to accomplish a specific goal.",
    )

    # Knowledge and Memory
    parser.add_argument(
        "--learn", help="Learn from a local directory or a Git repository URL."
    )
    parser.add_argument(
        "-r",
        "--read",
        action="append",
        help="Read a file and include its content in the context.",
    )

    # Task-specific Arguments
    parser.add_argument(
        "--git-commit",
        action="store_true",
        help="Generate a Git commit message based on the diff.",
    )
    parser.add_argument(
        "--gh-issue",
        help="Interact with a GitHub issue (e.g., 'summarize repo/owner#123').",
    )
    parser.add_argument(
        "-g",
        "--generate-image",
        action="store_true",
        help="Generate an image based on the prompt.",
    )
    parser.add_argument("-e", "--edit", help="Edit a file with a given prompt.")
    parser.add_argument(
        "--create-project",
        action="store_true",
        help="Create a new project structure based on a prompt.",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Generate installation commands based on a prompt.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Automatically confirm all prompts.",
    )

    # The main prompt for the agent or task
    parser.add_argument("prompt", nargs="*", help="The main prompt or instruction.")

    args = parser.parse_args()
    prompt = " ".join(args.prompt)

    # Handle --yes flag by monkeypatching user_confirm
    if args.yes:
        import utils.commands
        utils.commands.user_confirm = lambda msg: True

    # --- Mode Dispatcher ---

    if args.tui:
        tui_agent.main(initial_agent_prompt=prompt)
        sys.exit(0)

    if not config.API_KEY or config.API_KEY == "YOUR_GEMINI_API_KEY":
        print("Error: API_KEY is not set in config.py or as an environment variable.")
        sys.exit(1)
    genai.configure(api_key=config.API_KEY)

    try:
        models = {
            "default": genai.GenerativeModel(config.MODEL_NAME),
            "tools": genai.GenerativeModel(
                config.MODEL_NAME,
                safety_settings=config.SAFETY_SETTINGS,
                tools=list(tool_definitions.values()),
            ),
        }
        tasks.set_default_model(models["default"])
    except Exception as e:
        print(f"Model Initialization Error: {e}")
        sys.exit(1)

    initial_context = []
    if args.read:
        for f_path in args.read:
            try:
                with open(os.path.expanduser(f_path), "r") as f:
                    file_content = f.read()
                initial_context.append(
                    {
                        "role": "user",
                        "parts": [f"CONTEXT FILE: {f_path}\n{file_content}"],
                    }
                )
            except FileNotFoundError:
                print(f"Warning: File not found at {f_path}, skipping.")
            except Exception as e:
                print(f"Warning: Error reading file {f_path}: {e}")

    # --- Task Dispatcher ---

    if args.learn:
        if args.learn.startswith("http") and args.learn.endswith(".git"):
            from tools_mod.memory import learn_repo_task

            print(learn_repo_task(args.learn))
        else:
            print(db.learn_directory(args.learn))
        sys.exit(0)

    # If any specific task is provided, execute it.
    if args.git_commit:
        tasks.handle_git_commit(models["default"], prompt)
    elif args.gh_issue:
        tasks.handle_gh_issue(models["default"], args.gh_issue, prompt)
    elif args.generate_image:
        tasks.handle_image_generation(models["default"], prompt)
    elif args.create_project:
        tasks.handle_create_project(models["default"], prompt)
    elif args.install:
        tasks.handle_install(models["default"], prompt)
    elif args.edit:
        tasks.handle_edit_file(models["default"], args.edit, prompt)
    # If a prompt is provided (and not a specific task), default to the agentic mode.
    elif prompt:
        handle_agent_task(models, prompt, initial_context)
    else:
        # If no arguments are provided, print help.
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")
        sys.exit(0)
