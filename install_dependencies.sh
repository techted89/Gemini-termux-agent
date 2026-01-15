#!/bin/bash

# Check if running in Termux
if [[ -d "$HOME/.termux" ]]; then
    echo "🚀 Termux environment detected. Installing Termux-specific dependencies."

    # Update package lists
    pkg update -y

    # Install Python and essential build tools
    pkg install -y python python-pip clang make pkg-config libzmq

    # Install Python dependencies for Termux
    pip install -r requirements-termux.txt

else
    echo "🐧 Linux environment detected. Installing Linux dependencies."

    # Update package lists
    sudo apt-get update

    # Install pip for Python 3 and other essential packages
    sudo apt-get install -y python3-pip build-essential python3-dev pkg-config libzmq3-dev

    # Install other system-level dependencies
    sudo apt-get install -y libgl1

    # Install Python dependencies for Linux
    pip install -r requirements-linux.txt
fi

echo "✅ System dependencies and Python packages installed."
