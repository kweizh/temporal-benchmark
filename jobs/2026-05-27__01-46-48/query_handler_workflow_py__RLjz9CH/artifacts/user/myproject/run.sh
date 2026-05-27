#!/usr/bin/env bash
# run.sh – spin up the worker in the background, run the client, then clean up.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Resolve the python interpreter (prefer python3, fall back to python)
PYTHON=$(command -v python3 || command -v python)

# Start the worker in the background
"$PYTHON" worker.py &
WORKER_PID=$!

# Give the worker a moment to connect and start polling before the client fires
sleep 2

# Run the client; capture exit code so we can still kill the worker
set +e
"$PYTHON" client.py
CLIENT_EXIT=$?
set -e

# Shut down the worker gracefully
kill "$WORKER_PID" 2>/dev/null || true
wait "$WORKER_PID" 2>/dev/null || true

exit "$CLIENT_EXIT"
