import os
import sys
import difflib
from utils.commands import run_command, user_confirm
from utils.file_system import save_to_file
from api import call_gemini_api
from utils.display import display_image_termux
import config

_default_model = None


def set_default_model(model):
    global _default_model
    _default_model = model


def get_default_model():
    if _default_model is None:
        raise ValueError("Default model has not been set.")
    return _default_model


def handle_edit_file(model, filepath, prompt, save_as=None):
    try:
        with open(filepath, "r") as f:
            original_content = f.read()
    except FileNotFoundError:
        return f"Error: File not found at {filepath}"

    full_prompt = (
        f"CONTEXT:\n---\n{original_content}\n---\n"
        f"INSTRUCTION: Apply this change: '{prompt}'. "
        "IMPORTANT: Respond with ONLY the full code, including all original code that is not modified. "
        "Do not include any other conversational text, acknowledgment, or explanation. "
        "Your response will be written directly to a file."
    )

    new_content = call_gemini_api(
        model, [{"role": "user", "parts": [full_prompt]}]
    ).text

    # Clean up the response from the model
    if new_content.startswith("```") and new_content.endswith("```"):
        lines = new_content.split("\n")
        new_content = "\n".join(lines[1:-1])

    # Show a diff to the user
    diff = difflib.unified_diff(
        original_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"original: {filepath}",
        tofile=f"new: {save_as or filepath}",
    )

    print("--- PROPOSED CHANGES ---")
    for line in diff:
        # Simple color coding for the diff
        if line.startswith("+"):
            print(f"\033[92m{line}\033[0m", end="")
        elif line.startswith("-"):
            print(f"\033[91m{line}\033[0m", end="")
        else:
            print(line, end="")
    print("----------------------")

    if user_confirm("Apply these changes?"):
        target_path = save_as or filepath
        return save_to_file(target_path, new_content)
    return "Changes discarded."


def handle_create_project(model, prompt):
    structure_prompt = (
        f"Based on the following prompt, generate a project structure as a list of file paths. "
        f"For example: 'src/main.py', 'tests/test_main.py', 'README.md'.\n\nPROMPT: {prompt}"
    )

    file_list_str = call_gemini_api(
        model, [{"role": "user", "parts": [structure_prompt]}]
    ).text
    file_list = [line.strip() for line in file_list_str.split("\n") if line.strip()]

    print("Proposed project structure:")
    for file_path in file_list:
        print(f"- {file_path}")

    if user_confirm("Create this project structure?"):
        for file_path in file_list:
            try:
                # Create directories if they don't exist
                dir_name = os.path.dirname(file_path)
                if dir_name:
                    os.makedirs(dir_name, exist_ok=True)

                # Create an empty file
                with open(file_path, "w") as f:
                    pass  # Create empty file

            except Exception as e:
                print(f"Error creating {file_path}: {e}")
        return "Project structure created."
    return "Project creation cancelled."


def handle_git_commit(model, prompt=None):
    diff = run_command("git diff --cached", check_output=True)
    if not diff:
        return "No changes staged for commit. Use 'git add' to stage your changes."

    commit_prompt = (
        f"Based on the following git diff, generate a concise and descriptive commit message. "
        f"The message should follow conventional commit standards.\n\n"
        f"DIFF:\n---\n{diff}\n---\n"
    )

    if prompt:
        commit_prompt += f"USER HINT: {prompt}\n\n"

    commit_prompt += "COMMIT MESSAGE:"

    commit_message = call_gemini_api(
        model, [{"role": "user", "parts": [commit_prompt]}]
    ).text.strip()

    print(
        f"--- SUGGESTED COMMIT MESSAGE ---\n{commit_message}\n------------------------------"
    )

    if user_confirm("Use this commit message?"):
        # The commit message might have multiple lines, so we need to handle it carefully
        # We can save it to a temp file and use git commit -F <file>
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write(commit_message)
            tmp_path = tmp.name

        try:
            run_command(f"git commit -F {tmp_path}")
            return "Commit successful."
        finally:
            os.unlink(tmp_path)

    return "Commit cancelled."


def handle_gh_issue(model, repo, prompt):
    # This is a placeholder for a more complex GitHub integration
    # For now, it will just generate a comment based on the prompt
    comment_prompt = (
        f"Generate a GitHub issue comment for '{repo}' based on the prompt: '{prompt}'"
    )
    comment = call_gemini_api(model, [{"role": "user", "parts": [comment_prompt]}]).text

    print(f"--- GENERATED COMMENT ---\n{comment}\n-------------------------")
    if user_confirm("Post this comment?"):
        # Here you would add the actual GitHub API call
        return "Comment posted (simulation)."
    return "Comment discarded."


def handle_image_generation(model, prompt):
    # Placeholder for image generation
    print("Generating image...")
    # In a real scenario, you'd use a library like `stability-sdk` or `dalle-mini`
    # For now, we'll simulate it by creating a placeholder file

    # Create a unique filename
    import datetime

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(config.IMAGE_OUTPUT_DIR, f"img_{timestamp}.png")

    # Ensure the directory exists
    os.makedirs(config.IMAGE_OUTPUT_DIR, exist_ok=True)

    # Simulate creating an image file
    with open(filename, "w") as f:
        f.write(
            f"This is a placeholder for an image generated with the prompt: '{prompt}'"
        )

    display_image_termux(filename)

    return f"Image saved to {filename}"


def handle_install(model, prompt):
    install_prompt = (
        f"Based on the prompt '{prompt}', what are the installation commands? "
        f"Provide only the commands, each on a new line."
    )
    commands_str = call_gemini_api(
        model, [{"role": "user", "parts": [install_prompt]}]
    ).text
    commands = [cmd.strip() for cmd in commands_str.split("\n") if cmd.strip()]

    if not commands:
        return "Could not determine installation commands."

    print("--- PROPOSED COMMANDS ---")
    for cmd in commands:
        print(cmd)
    print("-------------------------")

    if user_confirm("Run these commands?"):
        for cmd in commands:
            run_command(cmd, shell=True)
        return "Commands executed."
    return "Installation cancelled."
