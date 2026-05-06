import os
import subprocess
import time
import pytest

PROJECT_DIR = "/home/user/reminder_project"

def test_workflow_execution():
    """Priority 1: Run the client script and verify the workflow executes correctly."""
    
    # Start the worker in the background
    worker_process = subprocess.Popen(
        ["npx", "ts-node", "src/worker.ts"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Give the worker a few seconds to connect to Temporal Cloud and start polling
    time.sleep(5)
    
    try:
        # Run the client script
        result = subprocess.run(
            ["npx", "ts-node", "src/client.ts"],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0, f"Client script failed: {result.stderr}"
        assert "Notified: Hello Temporal" in result.stdout, f"Expected 'Notified: Hello Temporal' in output, got: {result.stdout}"
        
    finally:
        # Clean up the worker process
        import signal
        os.killpg(os.getpgid(worker_process.pid), signal.SIGTERM)
        worker_process.wait(timeout=10)
