#!/bin/bash

if [ -d "/data/data/com.termux/files/home" ]; then
    # Termux Environment
    pkg update
    pkg install -y python

    # Use standard requirements for Termux
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    fi
else
    # Linux Environment
    sudo apt-get update
    sudo apt-get install -y python3-pip
    sudo apt-get install -y libgl1

    # Install linux specific requirements using the correct pip for python3
    REQUIREMENTS_FILE="requirements-linux.txt"
    if [ -f "$REQUIREMENTS_FILE" ]; then
        python3 -m pip install --break-system-packages -r "$REQUIREMENTS_FILE" || \
        python3 -m pip install -r "$REQUIREMENTS_FILE"
    else
        echo "Warning: $REQUIREMENTS_FILE not found, skipping Python dependencies"
    fi
fi
