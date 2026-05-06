import os
import subprocess
import time
import pytest
import signal
import socket

PROJECT_DIR = "/home/user/retry_project"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(5)
    return False

@pytest.fixture(scope="module")
def temporal_server():
    if "TEMPORAL_ADDRESS" in os.environ:
        # Use remote Temporal server
        yield
        return

    # Start local temporal server for testing
    process = subprocess.Popen(
        ["temporal", "server", "start-dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait for the temporal server to be ready on port 7233
    if not wait_for_port(7233, timeout=30):
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("Temporal dev server failed to start on port 7233.")
        
    yield
    
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

@pytest.fixture(scope="module")
def worker(temporal_server):
    # Start the worker
    process = subprocess.Popen(
        ["python3", "run_worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Give the worker a moment to connect and start polling
    time.sleep(5)
    
    yield process
    
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_workflow_execution(worker):
    # Run the workflow starter
    start_time = time.time()
    result = subprocess.run(
        ["python3", "start_workflow.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30
    )
    duration = time.time() - start_time
    
    # It should take at least 8 seconds (4 retries * 2s delay)
    assert duration >= 8, f"Workflow finished too quickly ({duration:.2f}s), expected at least 8s for 5 attempts with 2s delay."
    
    assert result.returncode == 0, f"start_workflow.py failed: {result.stderr}"
    assert "Failed as expected" in result.stdout, f"Expected 'Failed as expected' in output, got: {result.stdout}"

def test_retry_policy_configuration():
    # Verify the retry policy in the code
    workflow_file = os.path.join(PROJECT_DIR, "workflow.py")
    assert os.path.isfile(workflow_file), "workflow.py not found"
    
    with open(workflow_file, "r") as f:
        content = f.read()
        
    assert "maximum_attempts=5" in content.replace(" ", "") or "maximum_attempts=5" in content, "maximum_attempts=5 not found in workflow.py"
    assert "timedelta(seconds=2)" in content.replace(" ", "") or "timedelta(seconds=2)" in content, "initial_interval=timedelta(seconds=2) not found in workflow.py"
