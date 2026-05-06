import os
import subprocess
import time
import pytest

PROJECT_DIR = "/home/user/app"
LOG_FILE = os.path.join(PROJECT_DIR, "transactions.log")

@pytest.fixture(scope="module")
def start_worker():
    # Start the worker
    process = subprocess.Popen(
        ["python3", "run_worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Give the worker some time to connect and start polling
    time.sleep(5)

    yield

    # Shut down the worker
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_saga_failure_and_compensation(start_worker):
    """Verify that a failed deposit triggers the refund compensation."""
    # Ensure log file is clean before test
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    result = subprocess.run(
        ["python3", "run_workflow.py", "A_123", "B_FAIL", "100"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    assert os.path.exists(LOG_FILE), "transactions.log was not created."
    
    with open(LOG_FILE, "r") as f:
        content = f.read()
        
    assert "WITHDRAW A_123 100" in content, f"Expected WITHDRAW A_123 100 in log, got: {content}"
    assert "REFUND A_123 100" in content, f"Expected REFUND A_123 100 in log, got: {content}"
    assert "DEPOSIT B_FAIL 100" not in content, f"Did not expect DEPOSIT B_FAIL 100 in log, got: {content}"

def test_saga_success(start_worker):
    """Verify that a successful transfer does not trigger compensation."""
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    result = subprocess.run(
        ["python3", "run_workflow.py", "C_456", "D_789", "200"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    assert os.path.exists(LOG_FILE), "transactions.log was not created."
    
    with open(LOG_FILE, "r") as f:
        content = f.read()
        
    assert "WITHDRAW C_456 200" in content, f"Expected WITHDRAW C_456 200 in log, got: {content}"
    assert "DEPOSIT D_789 200" in content, f"Expected DEPOSIT D_789 200 in log, got: {content}"
    assert "REFUND" not in content, f"Did not expect REFUND in log for successful transfer, got: {content}"
