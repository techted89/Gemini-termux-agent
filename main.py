import google.generativeai as genai
import os
import sys
import argparse
import config
import tasks
import db
from agent import handle_agent_task
from api import call_gemini_api
from tools import tool_definitions, learn_repo_task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-y", "--yes", action="store_true", help="Auto-confirm all prompts")
    parser.add_argument("-A", "--agent", action="store_true")
    parser.add_argument("--learn")
    parser.add_argument("-r", "--read", action="append")
    parser.add_argument("prompt", nargs="*")
    # Add all other args from your dump here
    parser.add_argument("--git-commit", action="store_true")
    parser.add_argument("--gh-issue")
    parser.add_argument("-g", "--generate-image", action="store_true")
    parser.add_argument("-e", "--edit")
    parser.add_argument("--create-project", action="store_true")
    parser.add_argument("--install", action="store_true")
    parser.add_argument("-s", "--save")
    parser.add_argument("--deep-search", action="store_true")

    args = parser.parse_args()
    prompt = " ".join(args.prompt)

    if args.yes:
        import helpers
        helpers.AUTO_CONFIRM = True

    if not config.API_KEY:
        print("Error: API_KEY not set")
        sys.exit(1)
    genai.configure(api_key=config.API_KEY)

    try:
        def_model = genai.GenerativeModel(
            config.MODEL_NAME, safety_settings=config.SAFETY_SETTINGS
        )
        tasks.set_default_model(def_model)
        models = {
            "default": def_model,
            "tools": genai.GenerativeModel(
                config.MODEL_NAME,
                safety_settings=config.SAFETY_SETTINGS,
                tools=list(tool_definitions.values()),
            ),
        }
    except Exception as e:
        print(f"Init Error: {e}")
        sys.exit(1)

    ctx = []
    if args.read:
        for f in args.read:
            try:
                ctx.append(
                    {
                        "role": "user",
                        "parts": [f"FILE {f}:\n{open(os.path.expanduser(f)).read()}"],
                    }
                )
            except:
                pass

    if args.agent:
        if not prompt:
            print("Agent needs prompt")
            sys.exit(1)
        handle_agent_task(models, prompt, ctx)
        sys.exit(0)

    if args.learn:
        if args.learn.startswith("http"):
            db.learn_url(args.learn)
        else:
            learn_repo_task(args.learn)
        sys.exit(0)

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
        tasks.handle_edit_file(
            models["default"], args.edit, prompt, conversation_history=ctx
        )
    elif prompt:
        handle_agent_task(models, prompt, ctx)
    else:
        parser.print_help()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
