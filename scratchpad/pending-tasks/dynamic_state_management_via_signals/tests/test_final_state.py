import os
import subprocess
import time
import socket
import pytest

PROJECT_DIR = "/home/user/myproject"

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
    server_proc = subprocess.Popen(
        ["temporal", "server", "start-dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    if not wait_for_port(7233):
        import signal
        os.killpg(os.getpgid(server_proc.pid), signal.SIGTERM)
        pytest.fail("Temporal server failed to start on port 7233.")
    
    yield
    
    import signal
    os.killpg(os.getpgid(server_proc.pid), signal.SIGTERM)
    server_proc.wait(timeout=10)

@pytest.fixture(scope="module")
def worker(temporal_server):
    worker_proc = subprocess.Popen(
        ["python3", "run_worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    # Wait a bit for the worker to connect and start polling
    time.sleep(5)
    
    yield
    
    import signal
    os.killpg(os.getpgid(worker_proc.pid), signal.SIGTERM)
    worker_proc.wait(timeout=10)

def test_workflow_dynamic_state(worker):
    # Start the workflow
    start_res = subprocess.run(
        [
            "temporal", "workflow", "start",
            "--task-queue", "user-profile-tq",
            "--type", "UserProfileWorkflow",
            "--workflow-id", "test-user-profile-wf",
            "--input", '"test@example.com"'
        ],
        capture_output=True, text=True
    )
    assert start_res.returncode == 0, f"Failed to start workflow: {start_res.stderr}"
    
    # Wait for the workflow to be running
    time.sleep(2)
    
    # Query initial status
    query_res = subprocess.run(
        [
            "temporal", "workflow", "query",
            "--workflow-id", "test-user-profile-wf",
            "--type", "get_status"
        ],
        capture_output=True, text=True
    )
    assert query_res.returncode == 0, f"Failed to query status: {query_res.stderr}"
    assert '"active"' in query_res.stdout, f"Expected initial status 'active', got: {query_res.stdout}"
    
    # Signal update_status
    signal_res = subprocess.run(
        [
            "temporal", "workflow", "signal",
            "--workflow-id", "test-user-profile-wf",
            "--name", "update_status",
            "--input", '"suspended"'
        ],
        capture_output=True, text=True
    )
    assert signal_res.returncode == 0, f"Failed to signal update_status: {signal_res.stderr}"
    
    # Query updated status
    time.sleep(1)
    query_res2 = subprocess.run(
        [
            "temporal", "workflow", "query",
            "--workflow-id", "test-user-profile-wf",
            "--type", "get_status"
        ],
        capture_output=True, text=True
    )
    assert query_res2.returncode == 0, f"Failed to query updated status: {query_res2.stderr}"
    assert '"suspended"' in query_res2.stdout, f"Expected updated status 'suspended', got: {query_res2.stdout}"
    
    # Signal complete_workflow
    signal_res2 = subprocess.run(
        [
            "temporal", "workflow", "signal",
            "--workflow-id", "test-user-profile-wf",
            "--name", "complete_workflow"
        ],
        capture_output=True, text=True
    )
    assert signal_res2.returncode == 0, f"Failed to signal complete_workflow: {signal_res2.stderr}"
    
    time.sleep(2)
    
    # Get workflow result (this blocks until completion)
    result_res = subprocess.run(
        [
            "temporal", "workflow", "show",
            "--workflow-id", "test-user-profile-wf"
        ],
        capture_output=True, text=True
    )
    assert result_res.returncode == 0, f"Failed to get workflow result: {result_res.stderr}"
    assert 'COMPLETED' in result_res.stdout or 'Completed' in result_res.stdout, f"Expected final status 'COMPLETED', got: {result_res.stdout}"
    assert '"suspended"' in result_res.stdout, f"Expected final result 'suspended' in output, got: {result_res.stdout}"
