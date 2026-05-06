import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_pytest_passes():
    """Priority 3 fallback: Run the test suite to verify the workflow query implementation."""
    result = subprocess.run(
        ["pytest", "test_workflow.py"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, \
        f"pytest failed: {result.stdout}\n{result.stderr}"

def test_query_method_exists():
    """Check that the query method was actually added to the file."""
    workflow_path = os.path.join(PROJECT_DIR, "workflow.py")
    with open(workflow_path, "r") as f:
        content = f.read()
    
    assert "@workflow.query" in content, "The @workflow.query decorator is missing in workflow.py."
    assert "def get_email" in content, "The get_email method is missing in workflow.py."
