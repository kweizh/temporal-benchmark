import os
import subprocess
import time
import socket
import pytest

PROJECT_DIR = "/home/user/temporal-determinism"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module")
def setup_services():
    # Start Temporal server
    temporal_proc = subprocess.Popen(
        ["temporal", "server", "start-dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    if not wait_for_port(7233):
        import signal
        os.killpg(os.getpgid(temporal_proc.pid), signal.SIGTERM)
        pytest.fail("Temporal server failed to start on port 7233.")

    # Start mock HTTP server
    server_proc = subprocess.Popen(
        ["python3", "server.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    if not wait_for_port(8080):
        import signal
        os.killpg(os.getpgid(server_proc.pid), signal.SIGTERM)
        os.killpg(os.getpgid(temporal_proc.pid), signal.SIGTERM)
        pytest.fail("Mock server failed to start on port 8080.")

    # Start worker
    worker_proc = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    time.sleep(3) # Give worker a moment to connect and register

    yield

    # Teardown
    import signal
    try:
        os.killpg(os.getpgid(worker_proc.pid), signal.SIGTERM)
    except:
        pass
    try:
        os.killpg(os.getpgid(server_proc.pid), signal.SIGTERM)
    except:
        pass
    try:
        os.killpg(os.getpgid(temporal_proc.pid), signal.SIGTERM)
    except:
        pass

def test_workflow_execution_success(setup_services):
    result = subprocess.run(
        ["python3", "run_workflow.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Workflow execution failed: {result.stderr}\n{result.stdout}"
    assert "Workflow result:" in result.stdout, "Expected output from run_workflow.py"
    assert "success data" in result.stdout, "Expected 'success data' in the workflow result"

def test_workflow_py_refactored():
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    with open(workflow_path, "r") as f:
        content = f.read()
    
    assert "datetime.datetime.now" not in content, "datetime.now() should be removed from workflow.py"
    assert "uuid.uuid4" not in content, "uuid.uuid4() should be removed from workflow.py"
    assert "requests.get(" not in content, "requests.get() should be removed from workflow.py"
    
    assert "workflow.now" in content or "workflow.now()" in content, "workflow.now() should be used instead"
    assert "workflow.uuid4" in content or "workflow.uuid4()" in content, "workflow.uuid4() should be used instead"
    assert "workflow.execute_activity" in content, "Activity execution should be used for data fetching"

def test_activity_py_contains_fetch_data():
    activity_path = os.path.join(PROJECT_DIR, "activity.py")
    with open(activity_path, "r") as f:
        content = f.read()
    
    assert "fetch_data" in content, "fetch_data activity should be defined in activity.py"
    assert "requests.get(" in content, "requests.get() should be moved to activity.py"
