import os
import subprocess
import time
import pytest

PROJECT_DIR = "/home/user/temporal-hello"

def test_client_execution_and_output():
    # Install dependencies if not already done
    subprocess.run(["npm", "install"], cwd=PROJECT_DIR, check=True)

    # Start the worker in the background
    worker_proc = subprocess.Popen(
        ["npx", "ts-node", "src/worker.ts"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    try:
        # Give the worker a few seconds to connect to Temporal Cloud
        time.sleep(10)

        # Run the client
        client_result = subprocess.run(
            ["npx", "ts-node", "src/client.ts"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True
        )

        assert client_result.returncode == 0, f"Client script failed: {client_result.stderr}\n{client_result.stdout}"

        # Check output.log
        log_path = os.path.join(PROJECT_DIR, "output.log")
        assert os.path.exists(log_path), "output.log does not exist."

        with open(log_path, "r") as f:
            content = f.read().strip()

        assert content == "Hello, Temporal!", f"Expected 'Hello, Temporal!' in output.log, got: '{content}'"
    finally:
        # Shut down the worker
        import signal
        os.killpg(os.getpgid(worker_proc.pid), signal.SIGTERM)
        worker_proc.wait(timeout=10)
