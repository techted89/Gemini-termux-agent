import subprocess
import sys


def run_command(command, shell=False, check_output=False, ignore_errors=False):
    """Runs a shell command. Supports capturing output via check_output=True."""
    try:
        # Construct arguments for subprocess.run
        kwargs = {"check": True, "text": True, "shell": shell}

        # Only capture output if requested, otherwise let it print to screen
        if check_output:
            kwargs["capture_output"] = True

        result = subprocess.run(command, **kwargs)

        if check_output:
            return result.stdout.strip()
        return ""

    except subprocess.CalledProcessError as e:
        # If ignore_errors is True, return the error string instead of crashing
        if ignore_errors:
            return f"Error running command: {e}"

        # Otherwise, print to stderr and exit (Critical failure)
        print(f"Error running command: {command}\nSTDERR: {e.stderr}", file=sys.stderr)
        sys.exit(1)

    except FileNotFoundError:
        print(f"Error: Command not found: {command}", file=sys.stderr)
        sys.exit(1)


def user_confirm(question):
    """Asks the user for a yes/no confirmation."""
    while True:
        try:
            # Use print with end='' to ensure prompt appears before input wait
            print(f"{question} [y/n]: ", end="", flush=True)
            res = sys.stdin.readline().lower().strip()
            if res in ["y", "yes"]:
                return True
            if res in ["n", "no"]:
                return False
        except (EOFError, KeyboardInterrupt):
            return False
