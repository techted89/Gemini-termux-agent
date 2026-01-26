#!/bin/bash

# Update package lists
sudo apt-get update

# Install pip for Python 3
sudo apt-get install -y python3-pip

# Install other system-level dependencies
sudo apt-get install -y libgl1

# Install linux specific requirements using the correct pip for python3
REQUIREMENTS_FILE="requirements-linux.txt"
if [ -f "$REQUIREMENTS_FILE" ]; then
    python3 -m pip install --break-system-packages -r "$REQUIREMENTS_FILE" || \
    python3 -m pip install -r "$REQUIREMENTS_FILE"
else
    echo "Warning: $REQUIREMENTS_FILE not found, skipping Python dependencies"
fi
