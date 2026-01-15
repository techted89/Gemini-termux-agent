#!/bin/bash

# Update package lists
sudo apt-get update

# Install pip for Python 3
sudo apt-get install -y python3-pip

# Install other system-level dependencies
sudo apt-get install -y libgl1

# Install linux specific requirements using the correct pip for python3
python3 -m pip install -r requirements-linux.txt
