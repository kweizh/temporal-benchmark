#!/bin/bash
set -e

# Build TypeScript
npx tsc

# Start the worker in the background
node dist/worker.js &
WORKER_PID=$!

echo "Worker PID: $WORKER_PID"

# Give the worker a moment to connect and start polling
sleep 3

# Run the client
node dist/client.js
CLIENT_EXIT=$?

# Terminate the worker
kill $WORKER_PID 2>/dev/null || true
wait $WORKER_PID 2>/dev/null || true

exit $CLIENT_EXIT
