#!/usr/bin/env python3

import os
import subprocess
import sys

def is_termux():
    """Check if the script is running in a Termux environment."""
    return "com.termux" in os.environ.get("PREFIX", "")

def update_config(key, value):
    """Update a key in the config.py file."""
    with open("config.py", "r") as f:
        lines = f.readlines()

    with open("config.py", "w") as f:
        for line in lines:
            if line.startswith(key):
                f.write(f"{key} = \"{value}\"\n")
            else:
                f.write(line)

def setup_termux():
    """Interactive setup for Termux."""
    print("🚀 Termux environment detected. Configuring for client-server mode.")
    host = input("Enter the ChromaDB server IP address: ")
    port = input("Enter the ChromaDB server port (default: 8000): ") or "8000"

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
