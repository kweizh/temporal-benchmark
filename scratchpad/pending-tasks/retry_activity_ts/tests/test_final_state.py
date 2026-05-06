import os
import subprocess
import json
import time
import pytest

PROJECT_DIR = "/home/user/temporal-project"

@pytest.fixture(scope="module")
def setup_temporal():
    # Start temporal server
    temporal_server = subprocess.Popen(
        ["temporal", "server", "start-dev"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid
    )
    
    # Wait for temporal server to be ready
    time.sleep(5)
    
    # Start worker
    worker = subprocess.Popen(
        ["npm", "run", "start.watch"],
        cwd=PROJECT_DIR,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid
    )
    
    # Wait for worker to be ready
    time.sleep(5)
    
    # Run client
    subprocess.run(
        ["npm", "run", "start.client"],
        cwd=PROJECT_DIR,
        capture_output=True
    )
    
    yield
    
    # Teardown
    import signal
    os.killpg(os.getpgid(worker.pid), signal.SIGTERM)
    os.killpg(os.getpgid(temporal_server.pid), signal.SIGTERM)

def test_workflow_retry_policy(setup_temporal):
    """Priority 1: Use Temporal CLI to verify the workflow history and retry policy."""
    result = subprocess.run(
        ["temporal", "workflow", "show", "--workflow-id", "retry-workflow-id", "--output", "json"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"'temporal workflow show' failed: {result.stderr}"
    
    try:
        history = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Failed to parse temporal output as JSON: {result.stdout}")
    
    events = history.get("events", [])
    scheduled_event = None
    for event in events:
        if event.get("eventType") == "EVENT_TYPE_ACTIVITY_TASK_SCHEDULED":
            scheduled_event = event
            break
            
    assert scheduled_event is not None, "ActivityTaskScheduled event not found in workflow history."
    
    attrs = scheduled_event.get("activityTaskScheduledEventAttributes", {})
    retry_policy = attrs.get("retryPolicy", {})
    
    assert retry_policy.get("maximumAttempts") == 5, \
        f"Expected maximumAttempts to be 5, got: {retry_policy.get('maximumAttempts')}"
    
    assert retry_policy.get("initialInterval") == "2s", \
        f"Expected initialInterval to be '2s', got: {retry_policy.get('initialInterval')}"
        
    assert retry_policy.get("maximumInterval") == "2s", \
        f"Expected maximumInterval to be '2s', got: {retry_policy.get('maximumInterval')}"
        
    assert retry_policy.get("backoffCoefficient") == 1.0, \
        f"Expected backoffCoefficient to be 1.0, got: {retry_policy.get('backoffCoefficient')}"
