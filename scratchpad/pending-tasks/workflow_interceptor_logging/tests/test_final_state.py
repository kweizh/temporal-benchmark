import os
import subprocess
import time
import socket
import json
import pytest

PROJECT_DIR = "/home/user/project"
WORKFLOW_LOG = os.path.join(PROJECT_DIR, "workflow.log")
ACTIVITY_LOG = os.path.join(PROJECT_DIR, "activity.log")

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('localhost', port)) == 0:
                return True
        time.sleep(1)
    return False

@pytest.fixture(scope="module", autouse=True)
def run_temporal_workflow():
    # Remove existing logs if any
    if os.path.exists(WORKFLOW_LOG):
        os.remove(WORKFLOW_LOG)
    if os.path.exists(ACTIVITY_LOG):
        os.remove(ACTIVITY_LOG)

    # Start Temporal dev server
    temporal_server = subprocess.Popen(
        ["temporal", "server", "start-dev"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    if not wait_for_port(7233, timeout=30):
        import signal
        os.killpg(os.getpgid(temporal_server.pid), signal.SIGTERM)
        pytest.fail("Temporal dev server failed to start on port 7233.")

    # Start worker
    worker = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Give worker a moment to connect and register
    time.sleep(5)

    # Run starter
    starter = subprocess.run(
        ["python3", "starter.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        timeout=30
    )

    # Allow a moment for logs to be flushed
    time.sleep(2)

    yield starter

    # Teardown
    import signal
    os.killpg(os.getpgid(worker.pid), signal.SIGTERM)
    os.killpg(os.getpgid(temporal_server.pid), signal.SIGTERM)
    worker.wait(timeout=10)
    temporal_server.wait(timeout=10)

def test_workflow_execution_success(run_temporal_workflow):
    starter_result = run_temporal_workflow
    assert starter_result.returncode == 0, f"starter.py failed: {starter_result.stderr}"
    assert "Hello, Temporal!" in starter_result.stdout, "Expected successful workflow execution output."

def test_workflow_log_content():
    assert os.path.isfile(WORKFLOW_LOG), f"Workflow log file {WORKFLOW_LOG} does not exist."
    
    with open(WORKFLOW_LOG, 'r') as f:
        lines = f.readlines()
        
    assert len(lines) >= 1, "Workflow log file is empty."
    
    found = False
    for line in lines:
        try:
            data = json.loads(line.strip())
            if (data.get("event") == "WorkflowStarted" and 
                data.get("workflow_type") == "GreetingWorkflow" and 
                "workflow_id" in data):
                found = True
                break
        except json.JSONDecodeError:
            continue
            
    assert found, "Expected JSON object with WorkflowStarted event in workflow.log."

def test_activity_log_content():
    assert os.path.isfile(ACTIVITY_LOG), f"Activity log file {ACTIVITY_LOG} does not exist."
    
    with open(ACTIVITY_LOG, 'r') as f:
        lines = f.readlines()
        
    assert len(lines) >= 2, "Activity log file does not have enough entries."
    
    started_found = False
    completed_found = False
    
    for line in lines:
        try:
            data = json.loads(line.strip())
            if (data.get("event") == "ActivityStarted" and 
                data.get("activity_type") == "say_hello" and 
                data.get("args") == ["Temporal"]):
                started_found = True
            elif (data.get("event") == "ActivityCompleted" and 
                  data.get("activity_type") == "say_hello" and 
                  data.get("result") == "Hello, Temporal!"):
                completed_found = True
        except json.JSONDecodeError:
            continue
            
    assert started_found, "Expected JSON object with ActivityStarted event in activity.log."
    assert completed_found, "Expected JSON object with ActivityCompleted event in activity.log."
