import os
import subprocess
import json
import pytest

PROJECT_DIR = "/home/user/temporal-project"
RESULT_FILE = os.path.join(PROJECT_DIR, "result.txt")

def test_result_file_content():
    """Priority 3: Check the output file."""
    assert os.path.isfile(RESULT_FILE), f"Result file not found at {RESULT_FILE}"
    with open(RESULT_FILE, "r") as f:
        content = f.read()
    assert "Hello, World from child!" in content, \
        f"Expected result file to contain 'Hello, World from child!', got: {content}"

def test_parent_workflow_completed():
    """Priority 1: Use Temporal CLI to verify ParentWorkflow execution."""
    result = subprocess.run(
        ["temporal", "workflow", "list", "--query", "WorkflowType=\"ParentWorkflow\" AND ExecutionStatus=\"Completed\"", "-o", "json"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"temporal workflow list failed: {result.stderr}"
    
    output = result.stdout.strip()
    assert output, "No completed ParentWorkflow found."
    
    workflows = []
    for line in output.splitlines():
        try:
            workflows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
            
    if not workflows:
        try:
            workflows = json.loads(output)
        except json.JSONDecodeError:
            pass
            
    assert len(workflows) > 0, f"No completed ParentWorkflow found in JSON output: {output}"

def test_child_workflow_completed():
    """Priority 1: Use Temporal CLI to verify ChildWorkflow execution."""
    result = subprocess.run(
        ["temporal", "workflow", "list", "--query", "WorkflowType=\"ChildWorkflow\" AND ExecutionStatus=\"Completed\"", "-o", "json"],
        capture_output=True, text=True
    )
    assert result.returncode == 0, f"temporal workflow list failed: {result.stderr}"
    
    output = result.stdout.strip()
    assert output, "No completed ChildWorkflow found."
    
    workflows = []
    for line in output.splitlines():
        try:
            workflows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
            
    if not workflows:
        try:
            workflows = json.loads(output)
        except json.JSONDecodeError:
            pass
            
    assert len(workflows) > 0, f"No completed ChildWorkflow found in JSON output: {output}"
