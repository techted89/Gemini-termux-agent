import subprocess
import shutil
import sys
import os

# Check if binaries exist
GUM_BIN = shutil.which("gum")
GLOW_BIN = shutil.which("glow")

# If not found, check standard go bin path
if not GUM_BIN:
    home = os.path.expanduser("~")
    candidate = os.path.join(home, "go", "bin", "gum")
    if os.path.exists(candidate):
        GUM_BIN = candidate

if not GLOW_BIN:
    home = os.path.expanduser("~")
    candidate = os.path.join(home, "go", "bin", "glow")
    if os.path.exists(candidate):
        GLOW_BIN = candidate

def gum_input(placeholder="Type something...", prompt="> ", password=False):
    """Wraps `gum input`."""
    if not GUM_BIN:
        # Fallback
        try:
            return input(prompt)
        except EOFError:
            return ""

    cmd = [GUM_BIN, "input", "--placeholder", placeholder, "--prompt", prompt]
    if password:
        cmd.append("--password")

    # Run interactive
    # gum renders UI to stderr (or directly to tty).
    # We explicitly capture stdout to get the result, leaving stderr to flow to the terminal.
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE)
    return result.stdout.strip()

def gum_choose(options, header="Choose an option:", limit=1):
    """Wraps `gum choose`."""
    if not GUM_BIN:
        print(header)
        for i, opt in enumerate(options):
            print(f"{i+1}. {opt}")
        return input("Selection: ")

    cmd = [GUM_BIN, "choose", "--header", header, "--limit", str(limit)] + options
    # Capture only stdout for the selected value
    result = subprocess.run(cmd, text=True, stdout=subprocess.PIPE)
    return result.stdout.strip()

def gum_confirm(prompt="Are you sure?"):
    """Wraps `gum confirm`. Returns True for Yes, False for No."""
    if not GUM_BIN:
        res = input(f"{prompt} (y/n): ")
        return res.lower().startswith("y")

    cmd = [GUM_BIN, "confirm", prompt]
    # gum confirm returns 0 for yes, 1 for no
    result = subprocess.run(cmd)
    return result.returncode == 0

def gum_spin_command(command, title="Loading...", show_output=False):
    """Wraps `gum spin` around a shell command."""
    if not GUM_BIN:
        print(title)
        return subprocess.run(command, shell=True, text=True, capture_output=not show_output)

    # gum spin -- bash -c "command"
    cmd = [GUM_BIN, "spin", "--title", title, "--", "bash", "-c", command]

    # gum spin hides output of command by default?
    # It shows spinner while command runs.
    result = subprocess.run(cmd, text=True, capture_output=not show_output)
    return result

def glow_print(content):
    """Renders markdown using `glow`."""
    if not GLOW_BIN:
        print(content)
        return

    # Pipe content to glow
    # We use subprocess.run with input
    try:
        subprocess.run([GLOW_BIN, "-"], input=content, text=True)
    except Exception as e:
        print(f"Error running glow: {e}")
        print(content)

def gum_style(text, foreground="212", border="normal", padding="1 2", border_foreground="212"):
    """Wraps `gum style`."""
    if not GUM_BIN:
        print(text)
        return

    cmd = [
        GUM_BIN, "style",
        "--foreground", foreground,
        "--border", border,
        "--padding", padding,
        "--border-foreground", border_foreground,
        text
    ]
    subprocess.run(cmd)
