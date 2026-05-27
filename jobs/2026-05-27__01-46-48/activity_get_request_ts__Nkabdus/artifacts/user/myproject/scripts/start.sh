#!/usr/bin/env bash
# scripts/start.sh
#
# Orchestrates a full end-to-end run:
#   1. Start the Worker in the background so it can pick up workflow tasks.
#   2. Give it a few seconds to connect and begin polling.
#   3. Run the Client, which starts FetchUrlWorkflow and waits for the result.
#   4. Print the result (the Client already prints to stdout).
#   5. Terminate the Worker process cleanly and exit with the Client's exit code.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "[start.sh] Starting Temporal Worker in background ..."
npx ts-node src/worker.ts &
WORKER_PID=$!

# Give the Worker time to establish the gRPC connection to Temporal Cloud
# and begin polling before the Client tries to dispatch a workflow task.
sleep 5

echo "[start.sh] Running Temporal Client ..."
npx ts-node src/client.ts
CLIENT_EXIT=$?

echo "[start.sh] Client finished (exit $CLIENT_EXIT). Stopping Worker (PID $WORKER_PID) ..."
kill "$WORKER_PID" 2>/dev/null || true

# Wait for the worker to exit so we don't leave zombie processes.
wait "$WORKER_PID" 2>/dev/null || true

echo "[start.sh] Done."
exit $CLIENT_EXIT
