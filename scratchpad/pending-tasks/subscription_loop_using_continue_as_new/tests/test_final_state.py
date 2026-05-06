import os
import subprocess
import pytest
import asyncio
from temporalio.client import Client

PROJECT_DIR = "/home/user/subscription"

def test_starter_output():
    result = subprocess.run(
        ["python3", "starter.py"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"starter.py failed: {result.stderr}"
    assert "Subscription ended" in result.stdout, f"Expected \"Subscription ended\" in starter.py output, got: {result.stdout}"

def test_workflow_continued_as_new_via_cli():
    result = subprocess.run(
        ["temporal", "workflow", "show", "--workflow-id", "sub-workflow"],
        capture_output=True, text=True, cwd=PROJECT_DIR
    )
    assert result.returncode == 0, f"temporal CLI failed: {result.stderr}"
    assert "ContinuedAsNew" in result.stdout, "Expected WorkflowExecutionContinuedAsNew event in workflow history."

@pytest.mark.asyncio
async def test_cancellation_signal():
    # Connect to Temporal server
    client = await Client.connect("localhost:7233")
    
    # Start a new workflow execution
    handle = await client.start_workflow(
        "SubscriptionWorkflow",
        "cust-test-cancel", 60, 3, 0,
        id="sub-workflow-cancel",
        task_queue="subscription-task-queue"
    )
    
    # Send cancel signal
    await handle.signal("cancel_subscription")
    
    # Wait for result
    result = await handle.result()
    assert result == "Subscription cancelled", f"Expected \"Subscription cancelled\", got: {result}"
