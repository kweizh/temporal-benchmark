#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Ensure workspace directory exists
mkdir -p /workspace

# Start worker in the background
python3 worker.py &
WORKER_PID=$!

# Give worker a moment to connect and register
sleep 3

# Run the client to start the workflow and wait for completion
python3 client.py

# Shut down the worker
kill "$WORKER_PID" 2>/dev/null || true
wait "$WORKER_PID" 2>/dev/null || true

echo "Done. Check /workspace/attempts.log and /workspace/result.log"
