import os
import subprocess
import pytest

PROJECT_DIR = "/home/user/project"

def test_nondeterminism_removed():
    workflows_path = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    with open(workflows_path, "r") as f:
        content = f.read()
    
    assert "new Date()" not in content, "Expected 'new Date()' to be removed from workflows.ts."
    assert "globalDiscountState" not in content, "Expected 'globalDiscountState' to be removed from workflows.ts."

def test_workflow_now_used():
    workflows_path = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    with open(workflows_path, "r") as f:
        content = f.read()
    
    assert "workflow.now()" in content or ".now()" in content, "Expected 'workflow.now()' to be used in workflows.ts for time logic."

def test_workflow_execution_succeeds():
    # Make sure we can run the client and get a successful result
    # We will run the client which starts the workflow and waits for the result
    # The worker is assumed to be running in the background as per setup steps
    
    result = subprocess.run(
        ["npm", "run", "workflow"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    
    assert result.returncode == 0, f"'npm run workflow' failed: {result.stderr}"
    assert "Result:" in result.stdout, f"Expected 'Result:' in output, got: {result.stdout}"
