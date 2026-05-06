import os
import subprocess
import time
import signal
import pytest

PROJECT_DIR = "/home/user/project"

def test_workflow_execution():
    # Build the project
    build_result = subprocess.run(["npx", "tsc"], cwd=PROJECT_DIR, capture_output=True, text=True)
    assert build_result.returncode == 0, f"TypeScript build failed: {build_result.stderr}"

    # Start the worker in the background
    worker_process = subprocess.Popen(
        ["node", "lib/worker.js"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Give the worker a few seconds to connect to the Temporal server
    time.sleep(5)

    try:
        # Run the client
        client_result = subprocess.run(
            ["node", "lib/client.js"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=15
        )

        assert client_result.returncode == 0, f"Client script failed: {client_result.stderr}"
        assert "Hello, Temporal!" in client_result.stdout, f"Expected 'Hello, Temporal!' in output, got: {client_result.stdout}"

    finally:
        # Clean up the worker process
        os.killpg(os.getpgid(worker_process.pid), signal.SIGTERM)
        worker_process.wait(timeout=5)
