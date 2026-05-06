import os
import subprocess
import json
import pytest

PROJECT_DIR = "/home/user/project"
WORKFLOW_ID_FILE = os.path.join(PROJECT_DIR, "workflow_id.txt")

def test_workflow_id_file_exists():
    """Priority 3: Check that the workflow_id.txt file exists and contains the correct ID."""
    assert os.path.isfile(WORKFLOW_ID_FILE), f"File not found: {WORKFLOW_ID_FILE}"
    with open(WORKFLOW_ID_FILE, "r") as f:
        content = f.read().strip()
    assert "my-cron-workflow" in content, f"Expected 'my-cron-workflow' in {WORKFLOW_ID_FILE}, got: {content}"

def test_workflow_has_cron_schedule():
    """Priority 1: Use Temporal CLI to verify the workflow has the correct cron schedule."""
    result = subprocess.run(
        ["temporal", "workflow", "describe", "--workflow-id", "my-cron-workflow", "-o", "json"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"'temporal workflow describe' failed: {result.stderr}"
    
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail(f"Failed to parse JSON from temporal CLI output: {result.stdout}")
        
    execution_info = data.get("workflowExecutionInfo", {})
    # In JSON output, the cron schedule might be under executionInfo or executionConfig
    # We can also just check the raw JSON string if we are unsure of the exact path, 
    # but it's usually under workflowExecutionInfo.cronSchedule or executionConfig.cronSchedule
    # To be safe, let's just assert the cron string exists in the raw JSON output.
    assert "* * * * *" in result.stdout, f"Expected cron schedule '* * * * *' in workflow description, got: {result.stdout}"
