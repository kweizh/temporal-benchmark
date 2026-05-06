import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/temporal-project"

def test_workflow_uses_workflow_now():
    """Priority 3: Check file contents for workflow.now() and absence of datetime.now()."""
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    assert os.path.isfile(workflow_path), f"Workflow file {workflow_path} does not exist."
    with open(workflow_path, "r") as f:
        content = f.read()
    assert "datetime.now(" not in content, "Expected datetime.now() to be removed from workflow.py."
    assert "workflow.now(" in content, "Expected workflow.now() to be used in workflow.py."

def test_workflow_execution_succeeds():
    """Priority 3: Run the test script to verify the workflow works with Temporal Cloud."""
    # We require TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, TEMPORAL_API_KEY to be set
    env = os.environ.copy()
    assert "TEMPORAL_ADDRESS" in env, "TEMPORAL_ADDRESS is not set in environment."
    assert "TEMPORAL_NAMESPACE" in env, "TEMPORAL_NAMESPACE is not set in environment."
    assert "TEMPORAL_API_KEY" in env, "TEMPORAL_API_KEY is not set in environment."
    
    result = subprocess.run(
        ["python3", "test_workflow.py"],
        capture_output=True, text=True, cwd=PROJECT_DIR, env=env
    )
    assert result.returncode == 0, f"Running test_workflow.py failed: {result.stderr}"
    assert "Result: Hello, World! The time is" in result.stdout, f"Unexpected output: {result.stdout}"
