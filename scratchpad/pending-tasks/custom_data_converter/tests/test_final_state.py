import os
import subprocess
import time
import socket
import json
import pytest

PROJECT_DIR = "/home/user/temporal-project"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module", autouse=True)
def setup_and_run_workflow():
    # Start temporal server
    server_process = subprocess.Popen(
        ["temporal", "server", "start-dev", "--headless"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    if not wait_for_port(7233):
        import signal
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
        pytest.fail("Temporal server failed to start on port 7233.")
        
    # Start worker
    worker_process = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Give worker a moment to connect
    time.sleep(2)
    
    # Run starter
    starter_process = subprocess.run(
        ["python3", "starter.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    with open(os.path.join(PROJECT_DIR, "output.log"), "w") as f:
        f.write(starter_process.stdout)
        f.write(starter_process.stderr)
        
    yield
    
    # Cleanup
    import signal
    try:
        os.killpg(os.getpgid(worker_process.pid), signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        os.killpg(os.getpgid(server_process.pid), signal.SIGTERM)
    except ProcessLookupError:
        pass
    worker_process.wait(timeout=10)
    server_process.wait(timeout=10)

def test_workflow_output_correct():
    log_path = os.path.join(PROJECT_DIR, "output.log")
    with open(log_path, "r") as f:
        content = f.read()
    assert "Workflow result: Hello, Temporal!" in content, \
        f"Expected correct workflow output in output.log, got: {content}"

def test_payloads_are_base64_encoded():
    result = subprocess.run(
        ["temporal", "workflow", "show", "--workflow-id", "my-workflow", "--output", "json"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"'temporal workflow show' failed: {result.stderr}"
    
    # We can just check if the base64 encoded metadata string is in the JSON output
    # 'YmluYXJ5L2Jhc2U2NA==' is the base64 encoding of 'binary/base64'
    assert "YmluYXJ5L2Jhc2U2NA==" in result.stdout, \
        "Expected payload metadata 'encoding' to be 'binary/base64' (YmluYXJ5L2Jhc2U2NA== in JSON), but it was not found in the workflow history."
