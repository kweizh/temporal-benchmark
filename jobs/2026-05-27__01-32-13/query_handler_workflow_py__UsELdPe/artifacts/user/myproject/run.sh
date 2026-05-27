#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

python worker.py &
WORKER_PID=$!

cleanup() {
  if kill -0 "$WORKER_PID" 2>/dev/null; then
    kill "$WORKER_PID"
    wait "$WORKER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

sleep 2

python client.py
