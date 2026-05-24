#!/bin/bash
set -e

# Navigate to the project directory
cd /home/user/myproject

# Ensure /workspace exists and is writable
mkdir -p /workspace
chmod 777 /workspace

# Run the python script
python3 main.py
