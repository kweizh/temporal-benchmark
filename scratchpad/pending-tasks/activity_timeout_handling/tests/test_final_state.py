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

@pytest.fixture(scope="module")
def temporal_server():
    # Start temporal dev server
    process = subprocess.Popen(
        ["temporal", "server", "start-dev", "--headless"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    if not wait_for_port(7233):
        import signal
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        pytest.fail("Temporal server failed to start on port 7233.")

    yield

    # Shut down temporal server
    import signal
    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
    process.wait(timeout=10)

def test_workflow_execution(temporal_server):
    log_file = os.path.join(PROJECT_DIR, "output.log")
    with open(log_file, "w") as f:
        result = subprocess.run(
            ["python3", "run_workflow.py"],
            cwd=PROJECT_DIR,
            stdout=f,
            stderr=subprocess.STDOUT
        )
    
    assert result.returncode == 0, f"Workflow execution failed with exit code {result.returncode}. Check {log_file} for details."

    with open(log_file, "r") as f:
        output = f.read()
        assert "Processed sample_data" in output, f"Expected successful workflow output in log, got: {output}"

def test_workflow_timeouts_configured():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    with open(workflow_path, "r") as f:
        content = f.read()
    
    assert "start_to_close_timeout=timedelta(seconds=10)" in content or "start_to_close_timeout = timedelta(seconds=10)" in content, \
        "Expected start_to_close_timeout to be exactly 10 seconds."
    
    assert "schedule_to_close_timeout=timedelta(seconds=20)" in content or "schedule_to_close_timeout = timedelta(seconds=20)" in content, \
        "Expected schedule_to_close_timeout to be exactly 20 seconds."
