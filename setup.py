import os
import re
import socket
import tempfile
import shutil

CONFIG_FILE = "config.py"

def validate_host(host):
    """Validates that the host is a valid IP address or hostname."""
    if not host or not host.strip():
        return False
    # Remove spaces
    host = host.strip()
    try:
        # Check if it's a valid IP or resolvable hostname
        socket.gethostbyname(host)
        return True
    except socket.error:
        # Might be a local hostname not resolvable yet, but basic syntax check?
        # For simplicity, if it's not empty and has no spaces, we accept it if it looks like a host.
        # But socket.gethostbyname is a good check.
        # If the user is setting up for a VPS that is offline, this might fail.
        # Let's trust the user if it looks reasonable (no spaces).
        return " " not in host

def validate_port(port):
    """Validates that the port is an integer between 1 and 65535."""
    try:
        p = int(port)
        return 1 <= p <= 65535
    except ValueError:
        return False

def update_config(key, value):
    """
    Updates a key in config.py safely using atomic write and regex.
    """
    print(f"Updating {key} to {value}...")
    try:
        if not os.path.exists(CONFIG_FILE):
            print(f"Error: {CONFIG_FILE} not found.")
            return

        # Prepare the new line
        # Use repr to safely escape strings, but for numbers/bools we might want direct str()
        # The prompt said "serialize/escape the value safely (use Python repr() or json.dumps())"
        if isinstance(value, str):
            value_str = repr(value)
        else:
            value_str = str(value)

        new_line = f"{key} = {value_str}\n"

        # Create temp file
        temp_fd, temp_path = tempfile.mkstemp()

        key_found = False
        last_line_ends_with_newline = True

        with os.fdopen(temp_fd, 'w') as temp_file:
            with open(CONFIG_FILE, 'r') as original_file:
                for line in original_file:
                    # Regex match for "KEY =" or "KEY=" at start of line
                    if re.match(rf"^{re.escape(key)}\s*=", line):
                        temp_file.write(new_line)
                        key_found = True
                    else:
                        temp_file.write(line)
                    last_line_ends_with_newline = line.endswith('\n')

            if not key_found:
                # Append if not found
                if not last_line_ends_with_newline:
                     temp_file.write('\n')
                temp_file.write(new_line)

        # Atomic replace
        shutil.move(temp_path, CONFIG_FILE)
        print(f"Successfully updated {key}.")

    except Exception as e:
        print(f"Error updating config: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)

def setup_termux():
    print("Detected Termux/Linux environment. Configuring specific settings...")

    # Validation Loop for Host
    while True:
        host = input("Enter ChromaDB Host (default: localhost): ").strip()
        if not host:
            host = "localhost"

        if validate_host(host):
            break
        print("Invalid host. Please enter a valid hostname or IP address (no spaces).")

    # Validation Loop for Port
    while True:
        port = input("Enter ChromaDB Port (default: 8000): ").strip()
        if not port:
            port = "8000"

        if validate_port(port):
            break
        print("Invalid port. Please enter an integer between 1 and 65535.")

    update_config("CHROMA_HOST", host)
    update_config("CHROMA_PORT", int(port))

def main():
    if os.path.exists("/data/data/com.termux/files/home") or os.uname().sysname == "Linux":
        setup_termux()
    else:
        print("Standard setup.")
#!/usr/bin/env python3

import os
import subprocess
import sys
import re
import socket
import json
from tempfile import NamedTemporaryFile
from shutil import move

def is_termux():
    """Check if the script is running in a Termux environment."""
    return "com.termux" in os.environ.get("PREFIX", "")

def update_config(key, value):
    """Update a key in the config.py file."""
    config_path = "config.py"
    temp_file = NamedTemporaryFile(mode='w', delete=False, dir=os.path.dirname(config_path))

    key_found = False
    try:
        with open(config_path, "r") as f:
            for line in f:
                if re.match(f"^{key}\\s*=", line):
                    temp_file.write(f"{key} = {repr(value)}\n")
                    key_found = True
                else:
                    temp_file.write(line)

        if not key_found:
            temp_file.write(f"\n{key} = {repr(value)}\n")

        temp_file.close()
        move(temp_file.name, config_path)
    except IOError as e:
        print(f"Error updating config file: {e}")
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
        raise

def setup_termux():
    """Interactive setup for Termux."""
    print("🚀 Termux environment detected. Configuring for client-server mode.")

    while True:
        host = input("Enter the ChromaDB server IP address: ").strip()
        if not host or ' ' in host:
            print("Invalid host. Please enter a valid IP address or hostname.")
            continue
        try:
            socket.gethostbyname(host)
            break
        except socket.gaierror:
            print("Invalid host. Could not resolve hostname.")

    while True:
        port_str = input("Enter the ChromaDB server port (default: 8000): ").strip() or "8000"
        try:
            port = int(port_str)
            if 1 <= port <= 65535:
                break
            else:
                print("Invalid port. Please enter a number between 1 and 65535.")
        except ValueError:
            print("Invalid port. Please enter a number.")

    update_config("CHROMA_CLIENT_PROVIDER", "http")
    update_config("CHROMA_HOST", host)
    update_config("CHROMA_PORT", port)

    print("✅ Configuration updated for Termux.")

def setup_linux():
    """Interactive setup for Linux."""
    print("🐧 Linux environment detected. Configuring for local server mode.")

    update_config("CHROMA_CLIENT_PROVIDER", "local")

    print("✅ Configuration updated for Linux.")

def main():
    """Main setup function."""
    if is_termux():
        setup_termux()
    else:
        setup_linux()

if __name__ == "__main__":
    main()
