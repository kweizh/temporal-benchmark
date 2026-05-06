import os
import subprocess
import time
import socket
import pytest

PROJECT_DIR = "/home/user/project"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module")
def setup_environment():
    # Start Temporal dev server
    temporal_process = subprocess.Popen(
        ["temporal", "server", "start-dev", "--headless"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    if not wait_for_port(7233, timeout=30):
        import signal
        os.killpg(os.getpgid(temporal_process.pid), signal.SIGTERM)
        pytest.fail("Temporal server failed to start on port 7233.")

    # Start the worker
    worker_process = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    yield

    # Clean up processes
    import signal
    try:
        os.killpg(os.getpgid(worker_process.pid), signal.SIGTERM)
    except Exception:
        pass
    try:
        os.killpg(os.getpgid(temporal_process.pid), signal.SIGTERM)
    except Exception:
        pass

def test_asynchronous_activity_completion(setup_environment):
    # Remove existing files if any
    token_file = os.path.join(PROJECT_DIR, "task_token.txt")
    result_file = os.path.join(PROJECT_DIR, "result.txt")
    if os.path.exists(token_file):
        os.remove(token_file)
    if os.path.exists(result_file):
        os.remove(result_file)

    # Start the workflow
    starter_process = subprocess.Popen(
        ["python3", "starter.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for task_token.txt to be created
    start_time = time.time()
    token_created = False
    while time.time() - start_time < 30:
        if os.path.exists(token_file):
            token_created = True
            break
        time.sleep(1)
    
    assert token_created, "task_token.txt was not created within 30 seconds. The activity might not be running or failed to save the token."

    # Run the completion script
    completion_result = subprocess.run(
        ["python3", "complete_approval.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert completion_result.returncode == 0, f"complete_approval.py failed: {completion_result.stderr}"

    # Wait for starter.py to finish
    try:
        starter_stdout, starter_stderr = starter_process.communicate(timeout=30)
        assert starter_process.returncode == 0, f"starter.py failed: {starter_stderr.decode('utf-8')}"
    except subprocess.TimeoutExpired:
        starter_process.kill()
        pytest.fail("starter.py did not complete within 30 seconds after completion script was run.")

    # Verify result.txt
    assert os.path.exists(result_file), "result.txt was not created by starter.py."
    with open(result_file, "r") as f:
        content = f.read().strip()
    assert content == "APPROVED", f"Expected result.txt to contain 'APPROVED', but got: {content}"
