import os
import subprocess
import time
import socket
import pytest

PROJECT_DIR = "/home/user/project"

def wait_for_port(port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module")
def temporal_env():
    # Start the Temporal server
    server_process = subprocess.Popen(
        ["temporal", "server", "start-dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    if not wait_for_port(7233, timeout=30):
        import signal
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        pytest.fail("Temporal server failed to start and listen on port 7233.")

    # Start the worker
    worker_process = subprocess.Popen(
        ["python", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait a bit for the worker to initialize and connect to the server
    time.sleep(5)

    yield

    # Shut down the worker and server
    import signal
    try:
        os.killpg(os.getpgid(worker_process.pid), signal.SIGTERM)
        worker_process.wait(timeout=10)
    except Exception:
        pass

    try:
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        server_process.wait(timeout=10)
    except Exception:
        pass

def test_starter_output(temporal_env):
    """Priority 1: Run the starter script and verify its output."""
    starter_path = os.path.join(PROJECT_DIR, "starter.py")
    assert os.path.isfile(starter_path), f"starter.py not found at {starter_path}"

    result = subprocess.run(
        ["python", "starter.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0, f"'python starter.py' failed with error: {result.stderr}"
    assert "Hello Temporal" in result.stdout, f"Expected 'Hello Temporal' in output, got: {result.stdout}"
