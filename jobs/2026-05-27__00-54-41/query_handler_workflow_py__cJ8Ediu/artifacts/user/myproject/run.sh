#!/bin/bash
set -e

# Ensure temporalio is installed
pip install temporalio > /dev/null 2>&1 || true

# Run the python script
python main.py
