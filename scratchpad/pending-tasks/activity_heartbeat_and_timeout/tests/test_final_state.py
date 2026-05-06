import os
import subprocess
import time
import pytest

PROJECT_DIR = "/home/user/project"

@pytest.fixture(scope="module")
def worker_process():
    # Start the worker
    process = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Give the worker a moment to connect to Temporal
    time.sleep(3)
    
    yield process
    
    # Shut down the worker
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_workflow_execution(worker_process):
    # Run the starter script
    result = subprocess.run(
        ["python3", "start.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    # Check if starter script completed successfully
    assert result.returncode == 0, f"starter script failed: {result.stderr}"
    
    # Check output log
    log_file = os.path.join(PROJECT_DIR, "output.log")
    assert os.path.exists(log_file), f"Log file {log_file} does not exist."
    
    with open(log_file, "r") as f:
        content = f.read().strip()
        
    assert content == "SUCCESS", f"Expected log file to contain 'SUCCESS', got: '{content}'"

def test_activity_configuration():
    # Priority 3 fallback to check source code for correct timeout configurations
    workflow_file = os.path.join(PROJECT_DIR, "workflow.py")
    assert os.path.exists(workflow_file), f"workflow.py not found at {workflow_file}"
    
    with open(workflow_file, "r") as f:
        content = f.read()
        
    assert "start_to_close_timeout" in content, "Expected 'start_to_close_timeout' to be configured in workflow.py"
    assert "heartbeat_timeout" in content, "Expected 'heartbeat_timeout' to be configured in workflow.py"
