import os
import subprocess
import time
import socket
import json
import pytest

PROJECT_DIR = "/home/user/project"

def wait_for_port(port, timeout=60):
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(('127.0.0.1', port)) == 0:
                return True
        time.sleep(2)
    return False

@pytest.fixture(scope="module")
def temporal_env():
    # Start temporal dev server
    server_proc = subprocess.Popen(
        ["temporal", "server", "start-dev", "--headless", "--ip", "127.0.0.1"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    if not wait_for_port(7233):
        import signal
        os.killpg(os.getpgid(server_proc.pid), signal.SIGTERM)
        pytest.fail("Temporal server failed to start on port 7233")

    # Write worker.py
    worker_script = os.path.join(PROJECT_DIR, "worker.py")
    with open(worker_script, "w") as f:
        f.write('''import asyncio
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import ProcessItemsWorkflow

async def main():
    client = await Client.connect("localhost:7233")
    worker = Worker(
        client,
        task_queue="my-task-queue",
        workflows=[ProcessItemsWorkflow],
    )
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
''')

    worker_proc = subprocess.Popen(
        ["python3", "worker.py"],
        cwd=PROJECT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        preexec_fn=os.setsid
    )
    time.sleep(5) # Wait for worker to connect and start polling

    yield

    # Teardown
    import signal
    try:
        os.killpg(os.getpgid(worker_proc.pid), signal.SIGTERM)
    except Exception:
        pass
    try:
        os.killpg(os.getpgid(server_proc.pid), signal.SIGTERM)
    except Exception:
        pass

def test_workflow_execution(temporal_env):
    # Write test_workflow.py
    test_script = os.path.join(PROJECT_DIR, "test_workflow.py")
    with open(test_script, "w") as f:
        f.write('''import asyncio
import sys
from temporalio.client import Client

async def main():
    client = await Client.connect("localhost:7233")
    result = await client.execute_workflow(
        "ProcessItemsWorkflow",
        0, 250,
        id="test-workflow-1",
        task_queue="my-task-queue"
    )
    if result is True:
        print("SUCCESS")
    else:
        print("FAILED")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
''')
    
    # Run the workflow
    result = subprocess.run(
        ["python3", "test_workflow.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, f"Workflow execution failed: {result.stderr}"
    assert "SUCCESS" in result.stdout, f"Workflow did not return True. Output: {result.stdout}"

    # Verify continue_as_new using CLI
    # If continue_as_new was called twice, there should be 3 executions for this workflow ID
    cli_result = subprocess.run(
        ["temporal", "workflow", "list", "-q", 'WorkflowId="test-workflow-1"', "--output", "json"],
        capture_output=True,
        text=True
    )
    assert cli_result.returncode == 0, f"Failed to list workflows: {cli_result.stderr}"
    
    executions = json.loads(cli_result.stdout)
    assert len(executions) >= 3, f"Expected at least 3 executions (2 continue_as_new calls), but found {len(executions)}. The workflow might not be using continue_as_new correctly."
