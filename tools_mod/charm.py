import subprocess
import os
import shutil

def _check_dependency(cmd):
    if not shutil.which(cmd):
        raise EnvironmentError(f"Required command '{cmd}' not found. Please install it (e.g., via 'go install github.com/charmbracelet/{cmd}@latest').")

def gum_confirm(prompt, default=True):
    """
    Prompts the user for confirmation using `gum confirm`.
    """
    _check_dependency("gum")
    cmd = ["gum", "confirm", prompt]
    if not default:
        cmd.append("--default=No")

    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def gum_input(placeholder, value=""):
    """
    Prompts the user for input using `gum input`.
    """
    _check_dependency("gum")
    cmd = ["gum", "input", "--placeholder", placeholder, "--value", value]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    return result.stdout.strip()

def gum_choose(options, header=None, limit=1):
    """
    Prompts the user to choose from a list of options using `gum choose`.
    """
    _check_dependency("gum")
    cmd = ["gum", "choose"]
    if header:
        cmd.extend(["--header", header])
    if limit > 1:
        cmd.extend(["--limit", str(limit)])

    # Pass options via stdin
    input_str = "\n".join(options)
    result = subprocess.run(cmd, input=input_str, stdout=subprocess.PIPE, text=True)

    if limit == 1:
        return result.stdout.strip()
    else:
        return [line for line in result.stdout.splitlines() if line]

def glow_render(text):
    """
    Renders markdown text using `glow`.
    """
    # If glow is missing, return plain text
    if not shutil.which("glow"):
        return text

    cmd = ["glow", "-"]
    result = subprocess.run(cmd, input=text, stdout=subprocess.PIPE, text=True)
    return result.stdout
