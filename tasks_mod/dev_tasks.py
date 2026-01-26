import os
import difflib
from utils.commands import run_command, user_confirm
from utils.file_system import save_to_file
from utils.display import display_image
from api import call_gemini_api
import config

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

    display_image(filename)

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
