import os
import subprocess
import time
import pytest
import signal

PROJECT_DIR = "/home/user/project"

@pytest.fixture(scope="module")
def start_worker():
    # Start the worker process
    worker_process = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait for the worker to connect and start listening
    time.sleep(5)
    
    # Check if worker crashed immediately
    if worker_process.poll() is not None:
        stdout, stderr = worker_process.communicate()
        pytest.fail(f"Worker process exited prematurely with code {worker_process.returncode}.\nStdout: {stdout.decode()}\nStderr: {stderr.decode()}")
        
    yield worker_process
    
    # Shut down the worker process
    try:
        os.killpg(os.getpgid(worker_process.pid), signal.SIGTERM)
        worker_process.wait(timeout=10)
    except Exception:
        pass

def test_workflow_execution(start_worker):
    """Priority 1: Use the user's start.py script to execute the workflow and verify the result."""
    result = subprocess.run(
        ["python3", "start.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30
    )
    
    assert result.returncode == 0, f"'python3 start.py' failed with exit code {result.returncode}.\nStderr: {result.stderr}\nStdout: {result.stdout}"
    
    expected_output = "RESULT: Notified: Time is up!"
    assert expected_output in result.stdout, f"Expected output to contain '{expected_output}', but got:\n{result.stdout}"
