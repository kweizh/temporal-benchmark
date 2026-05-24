#!/bin/bash

# Start the worker in the background
python3 worker.py > worker.log 2>&1 &
WORKER_PID=$!

# Give the worker a moment to start
sleep 2

# Run the client and capture its output
python3 client.py

# Kill the worker
kill $WORKER_PID

# Wait for worker to exit
wait $WORKER_PID 2>/dev/null || true
