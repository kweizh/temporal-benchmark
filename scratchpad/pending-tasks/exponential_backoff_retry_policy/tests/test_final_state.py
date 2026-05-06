import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_workflow_pytest_passes():
    """Priority 1/3: Run pytest to verify the workflow execution behaves as expected."""
    result = subprocess.run(
        ["pytest", "test_workflow.py"],
        capture_output=True,
        text=True,
        cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"pytest failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"

def test_retry_policy_in_workflow_code():
    """Priority 3: Verify the source code explicitly contains the required RetryPolicy parameters."""
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    with open(workflow_path, "r") as f:
        content = f.read()
    
    assert "RetryPolicy" in content, "RetryPolicy is not used in workflow.py."
    assert "initial_interval" in content, "initial_interval is not set in RetryPolicy."
    assert "backoff_coefficient=2.0" in content.replace(" ", ""), "backoff_coefficient=2.0 is not set in RetryPolicy."
    assert "maximum_attempts=3" in content.replace(" ", ""), "maximum_attempts=3 is not set in RetryPolicy."
