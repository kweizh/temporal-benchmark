#!/usr/bin/env bash
set -euo pipefail

# Ensure the log directory exists and is writable
mkdir -p /workspace

# Run the combined worker+client entrypoint and exit with its exit code
exec python3 main.py
