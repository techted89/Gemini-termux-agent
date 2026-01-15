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
