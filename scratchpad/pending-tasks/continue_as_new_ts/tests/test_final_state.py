import os
import subprocess
import time
import pytest
import json

PROJECT_DIR = "/home/user/project"

@pytest.fixture(scope="module")
def run_workflow():
    # Start worker
    worker_process = subprocess.Popen(
        ["npm", "run", "start.worker"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )

    # Wait a bit for worker to start
    time.sleep(5)

    # Start client
    client_process = subprocess.run(
        ["npm", "run", "start.client"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )

    yield client_process

    # Kill worker
    import signal
    os.killpg(os.getpgid(worker_process.pid), signal.SIGTERM)
    worker_process.wait(timeout=10)

def test_workflow_returns_1000(run_workflow):
    client_process = run_workflow
    assert client_process.returncode == 0, f"Client failed: {client_process.stderr}"
    assert "Result: 1000" in client_process.stdout, f"Expected 'Result: 1000' in output, got: {client_process.stdout}"

def test_workflow_used_continue_as_new(run_workflow):
    # Read workflow ID from the file written by client
    wf_id_file = os.path.join(PROJECT_DIR, "workflow_id.txt")
    assert os.path.exists(wf_id_file), "workflow_id.txt not found"
    
    with open(wf_id_file) as f:
        wf_id = f.read().strip()

    # Use Temporal CLI to get the history
    cmd = ["temporal", "workflow", "show", "--workflow-id", wf_id, "--output", "json"]
    
    # temporal cli supports TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY from environment
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Failed to get workflow history: {result.stderr}"
    
    # The output of `temporal workflow show` might contain ContinuedAsNew
    # Or we can just grep the text output if we don't use --output json
    # Let's just run without --output json and check text
    cmd_text = ["temporal", "workflow", "show", "--workflow-id", wf_id]
    result_text = subprocess.run(cmd_text, capture_output=True, text=True)
    
    assert "WorkflowExecutionContinuedAsNew" in result_text.stdout or "ContinuedAsNew" in result_text.stdout, \
        f"Expected WorkflowExecutionContinuedAsNew in workflow history, but it was not found. This means continueAsNew was not used. History: {result_text.stdout}"
