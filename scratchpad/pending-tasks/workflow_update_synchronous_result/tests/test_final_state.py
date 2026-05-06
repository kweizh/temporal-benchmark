import os
import subprocess
import time
import socket
import pytest

PROJECT_DIR = "/home/user/temporal-counter"

def wait_for_port(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module")
def temporal_server():
    # Start Temporal server
    process = subprocess.Popen(
        ["temporal", "server", "start-dev", "--headless"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    if not wait_for_port(7233, timeout=60):
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("Temporal server failed to start on port 7233.")
        
    yield
    
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=30)

@pytest.fixture(scope="module")
def temporal_worker(temporal_server):
    # Start the user's worker
    worker_env = os.environ.copy()
    worker_env["PYTHONPATH"] = PROJECT_DIR
    process = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        env=worker_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait a few seconds for the worker to connect
    time.sleep(5)
    
    # Check if worker died immediately
    if process.poll() is not None:
        stdout, stderr = process.communicate()
        pytest.fail(f"Worker failed to start. stdout: {stdout}, stderr: {stderr}")
        
    yield
    
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=30)

def test_client_script_output(temporal_worker):
    """Run the client script and verify it prints 5."""
    result = subprocess.run(
        ["python3", "client.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"client.py failed: {result.stderr}"
    assert "5" in result.stdout, f"Expected output to contain '5', got: {result.stdout}"

def test_validator_rejects_negative_amount(temporal_worker):
    """Verify that sending a negative amount to the update is rejected by the validator."""
    test_script = os.path.join(PROJECT_DIR, "test_validator.py")
    with open(test_script, "w") as f:
        f.write("""
import asyncio
from temporalio.client import Client, WorkflowUpdateFailedError

async def main():
    client = await Client.connect("localhost:7233")
    handle = client.get_workflow_handle("counter-workflow")
    try:
        await handle.execute_update("add", -1)
        print("SUCCESS_BUT_SHOULD_FAIL")
    except WorkflowUpdateFailedError as e:
        print(f"FAILED_AS_EXPECTED: {e}")
    except Exception as e:
        print(f"OTHER_ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
""")
    
    result = subprocess.run(
        ["python3", "test_validator.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    os.remove(test_script)
    
    assert "FAILED_AS_EXPECTED" in result.stdout, f"Validator did not reject negative amount as expected. Output: {result.stdout}\nStderr: {result.stderr}"
    assert "SUCCESS_BUT_SHOULD_FAIL" not in result.stdout, "Validator allowed negative amount!"
