import os
import subprocess
import time
import pytest
import signal

PROJECT_DIR = "/home/user/project"
LOG_FILE = "/home/user/project/output.log"

@pytest.fixture(scope="module")
def run_workflow():
    # Remove log file if exists to ensure a fresh run
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        
    # Start the worker
    worker_process = subprocess.Popen(
        ["npx", "ts-node", "src/worker.ts"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Give the worker a few seconds to connect and start polling
    time.sleep(5)
    
    # Run the client script
    client_result = subprocess.run(
        ["npx", "ts-node", "src/client.ts"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    # Shut down the worker
    os.killpg(os.getpgid(worker_process.pid), signal.SIGTERM)
    worker_process.wait(timeout=10)
    
    return client_result

def test_client_script_success(run_workflow):
    """Priority 3: Verify the client script executes without error."""
    client_result = run_workflow
    assert client_result.returncode == 0, \
        f"Client script failed to execute: {client_result.stderr}\nStdout: {client_result.stdout}"

def test_output_log_contains_canceled(run_workflow):
    """Priority 3: Verify the workflow returns 'Canceled' and logs it."""
    assert os.path.isfile(LOG_FILE), \
        f"Log file {LOG_FILE} was not created by the client script."
        
    with open(LOG_FILE, "r") as f:
        content = f.read()
        
    assert "Canceled" in content, \
        f"Expected 'Canceled' in {LOG_FILE}, got: {content}"