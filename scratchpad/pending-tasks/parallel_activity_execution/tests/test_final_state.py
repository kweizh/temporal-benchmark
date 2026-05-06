import os
import subprocess
import pytest
import time

PROJECT_DIR = "/home/user/temporal_project"

@pytest.fixture(scope="module")
def setup_temporal_env():
    # Start the worker process
    worker_process = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    
    # Wait a moment for worker to connect
    time.sleep(2)
    
    yield
    
    # Shut down the worker
    import signal
    os.killpg(os.getpgid(worker_process.pid), signal.SIGTERM)
    worker_process.wait(timeout=10)

def test_starter_output(setup_temporal_env):
    """Priority 1: Run the starter script and verify its output."""
    result = subprocess.run(
        ["python3", "starter.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    
    assert result.returncode == 0, f"starter.py execution failed: {result.stderr}"
    
    expected_output = "['Processed 1', 'Processed 2', 'Processed 3', 'Processed 4', 'Processed 5']"
    assert expected_output in result.stdout, \
        f"Expected output to contain {expected_output}, but got: {result.stdout}"

def test_workflow_history_shows_parallelism(setup_temporal_env):
    """Priority 1: Use Temporal CLI to verify history events show concurrent scheduling."""
    # Note: We assume starter.py starts the workflow and waits for it, so it's already in the history.
    # We can fetch the latest workflow execution on the task queue 'parallel-tasks'
    result = subprocess.run(
        ["temporal", "workflow", "list", "--query", "TaskQueue='parallel-tasks'", "--json"],
        capture_output=True,
        text=True
    )
    
    import json
    try:
        workflows = json.loads(result.stdout)
    except Exception as e:
        # If no json output, we just skip the CLI test or fail gracefully
        pytest.fail(f"Failed to parse temporal cli output: {result.stdout}")
        
    assert len(workflows) > 0, "No workflows found in 'parallel-tasks' task queue."
    
    workflow_id = workflows[0]["execution"]["workflowId"]
    run_id = workflows[0]["execution"]["runId"]
    
    history_result = subprocess.run(
        ["temporal", "workflow", "show", "--workflow-id", workflow_id, "--run-id", run_id, "--json"],
        capture_output=True,
        text=True
    )
    
    assert history_result.returncode == 0, f"Failed to get history for {workflow_id}"
    
    # Check that multiple ActivityTaskScheduled events appear before any ActivityTaskStarted
    # This indicates they were scheduled concurrently.
    scheduled_count = 0
    started_count = 0
    events = history_result.stdout.splitlines()
    
    for line in events:
        if not line.strip():
            continue
        try:
            event = json.loads(line)
            event_type = event.get("eventType")
            if event_type == "EVENT_TYPE_ACTIVITY_TASK_SCHEDULED":
                scheduled_count += 1
            elif event_type == "EVENT_TYPE_ACTIVITY_TASK_STARTED":
                started_count += 1
                
                # If we see a start event, we should have already scheduled multiple activities
                # if they were done in parallel. In sequential, we schedule 1, start 1, complete 1.
                # In parallel, we schedule 5, then start them.
                if scheduled_count > 1:
                    break
        except:
            pass
            
    assert scheduled_count > 1, "Activities were not scheduled concurrently (found sequential execution)."