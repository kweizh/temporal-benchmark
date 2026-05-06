import os
import subprocess
import time
import socket
import pytest

PROJECT_DIR = "/home/user/temporal_project"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module", autouse=True)
def start_temporal_and_worker():
    # Start Temporal dev server
    temporal_proc = subprocess.Popen(
        ["temporal", "server", "start-dev", "--headless"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    if not wait_for_port(7233):
        import signal
        os.killpg(os.getpgid(temporal_proc.pid), signal.SIGTERM)
        pytest.fail("Temporal server failed to start.")

    # Start the worker
    worker_proc = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait a bit for worker to register
    time.sleep(3)

    yield

    # Shut down worker and temporal server
    import signal
    os.killpg(os.getpgid(worker_proc.pid), signal.SIGTERM)
    os.killpg(os.getpgid(temporal_proc.pid), signal.SIGTERM)
    worker_proc.wait(timeout=10)
    temporal_proc.wait(timeout=10)

def test_verify_replay_succeeds():
    """Verify that the old workflow history replays successfully."""
    result = subprocess.run(
        ["python3", "verify_replay.py"],
        cwd=PROJECT_DIR,
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Replaying history failed. Error: {result.stderr}\nOutput: {result.stdout}"

def test_new_workflow_succeeds_and_returns_new_result():
    """Verify that starting a new workflow uses the new activity and returns new_result."""
    result = subprocess.run(
        ["python3", "test_new_workflow.py"],
        cwd=PROJECT_DIR,
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"Starting new workflow failed. Error: {result.stderr}\nOutput: {result.stdout}"
    assert "New workflow successful!" in result.stdout, f"Expected success message not found. Output: {result.stdout}"

def test_workflow_patched_is_used():
    """Check if workflow.patched is used in workflow.py"""
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    with open(workflow_path, "r") as f:
        content = f.read()
    
    assert "workflow.patched" in content, "You must use `workflow.patched` to migrate the workflow."
