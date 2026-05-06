import os
import subprocess
import time
import pytest
import json

PROJECT_DIR = "/home/user/project"

@pytest.fixture(scope="module")
def temporal_env():
    # Start Temporal dev server
    server_proc = subprocess.Popen(
        ["temporal", "server", "start-dev", "--headless"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait for server to be ready
    time.sleep(5)
    
    # Start worker
    worker_proc = subprocess.Popen(
        ["npm", "start"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait for worker to connect
    time.sleep(5)
    
    yield
    
    # Cleanup
    import signal
    try:
        os.killpg(os.getpgid(worker_proc.pid), signal.SIGTERM)
    except:
        pass
    try:
        os.killpg(os.getpgid(server_proc.pid), signal.SIGTERM)
    except:
        pass

def test_workflow_uses_patch(temporal_env):
    # Run the client to start and wait for workflow
    result = subprocess.run(
        ["npm", "run", "workflow"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Workflow execution failed: {result.stderr}\n{result.stdout}"
    
    # Extract workflow ID from output
    # e.g. "Started workflow workflow-0.12345"
    wf_id = None
    for line in result.stdout.split('\n'):
        if "Started workflow" in line:
            wf_id = line.split()[-1]
            break
            
    assert wf_id is not None, f"Could not find workflowId in output: {result.stdout}"
    
    # Verify using Temporal CLI
    history_result = subprocess.run(
        ["temporal", "workflow", "show", "--workflow-id", wf_id, "--output", "json"],
        capture_output=True,
        text=True
    )
    assert history_result.returncode == 0, f"Failed to get workflow history: {history_result.stderr}"
    
    # Parse history to find ActivityTaskScheduled events
    history = json.loads(history_result.stdout)
    events = history.get("events", [])
    
    activity_names = []
    for event in events:
        if event.get("eventType") == "EVENT_TYPE_ACTIVITY_TASK_SCHEDULED":
            attrs = event.get("activityTaskScheduledEventAttributes", {})
            activity_type = attrs.get("activityType", {}).get("name")
            if activity_type:
                activity_names.append(activity_type)
                
    assert "chargeCustomerV2" in activity_names, f"Expected chargeCustomerV2 in history, got: {activity_names}"
    assert "chargeCustomer" not in activity_names, f"Did not expect chargeCustomer in history, got: {activity_names}"

def test_code_contains_patched():
    wf_path = os.path.join(PROJECT_DIR, "src/workflows.ts")
    with open(wf_path) as f:
        content = f.read()
        
    assert "patched(" in content or "patched ('" in content or "patched(\"" in content, "Expected 'patched' API to be used in src/workflows.ts"
    assert "use-v2-charge" in content, "Expected patch ID 'use-v2-charge' to be used."
