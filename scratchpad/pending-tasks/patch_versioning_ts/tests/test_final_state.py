import asyncio
import os
import re
import socket
import subprocess
import time

import pytest
from xprocess import ProcessStarter

PROJECT_DIR = "/home/user/myproject"
RUN_ID = os.environ["ZEALT_RUN_ID"]
OLD_WF_ID = f"order-old-{RUN_ID}"
NEW_WF_ID = f"order-new-{RUN_ID}"
TASK_QUEUE = "order-ts"

NOTIFY_LOG = "/workspace/notify.log"
ORDER_LOG = "/workspace/order.log"


@pytest.fixture(scope="session", autouse=True)
def start_old_workflow():
    """Run the pre-patch helper that registers and starts the OLD workflow execution
    BEFORE the agent's worker (which contains the patched code) is started.

    The helper is shipped under /opt/prepatch and uses the unpatched workflow code so
    that the history written for order-old-${ZEALT_RUN_ID} does not contain a
    'add-notify-customer' patch marker.
    """
    # Clean shared log files.
    for path in (NOTIFY_LOG, ORDER_LOG):
        try:
            os.remove(path)
        except FileNotFoundError:
            pass

    result = subprocess.run(
        ["node", "/opt/prepatch/dist/start_old.js"],
        capture_output=True,
        text=True,
        env=os.environ.copy(),
        timeout=180,
    )
    assert result.returncode == 0, (
        f"Pre-patch worker failed to start old workflow.\n"
        f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    yield


@pytest.fixture(scope="session")
def start_agent_worker(xprocess, start_old_workflow):
    """Start the agent's worker via `npm start`."""

    class Starter(ProcessStarter):
        name = "agent_worker"
        # The agent's worker should log a readiness message containing "Worker started".
        pattern = "Worker started"
        args = ["npm", "start"]
        env = os.environ.copy()
        popen_kwargs = {"cwd": PROJECT_DIR, "text": True}
        timeout = 180
        terminate_on_interrupt = True

    xprocess.ensure(Starter.name, Starter)
    yield
    info = xprocess.getinfo(Starter.name)
    info.terminate()


def _client():
    from temporalio.client import Client

    return Client.connect(
        os.environ["TEMPORAL_ADDRESS"],
        namespace=os.environ["TEMPORAL_NAMESPACE"],
        api_key=os.environ["TEMPORAL_API_KEY"],
        tls=True,
    )


async def _start_new_workflow():
    client = await _client()
    handle = await client.start_workflow(
        "OrderWorkflow",
        NEW_WF_ID,
        id=NEW_WF_ID,
        task_queue=TASK_QUEUE,
    )
    return handle


async def _wait_for_completed(workflow_id: str, timeout_s: int = 180) -> str:
    from temporalio.client import Client, WorkflowExecutionStatus

    client = await _client()
    deadline = time.time() + timeout_s
    last_status = None
    while time.time() < deadline:
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()
        last_status = desc.status
        if desc.status == WorkflowExecutionStatus.COMPLETED:
            return "COMPLETED"
        if desc.status in (
            WorkflowExecutionStatus.FAILED,
            WorkflowExecutionStatus.CANCELED,
            WorkflowExecutionStatus.TERMINATED,
            WorkflowExecutionStatus.TIMED_OUT,
        ):
            return desc.status.name
        await asyncio.sleep(2)
    return f"TIMEOUT(last={last_status})"


def test_workflows_ts_contains_patched_marker():
    path = os.path.join(PROJECT_DIR, "src", "workflows.ts")
    with open(path) as f:
        content = f.read()
    assert re.search(r"patched\(\s*['\"]add-notify-customer['\"]\s*\)", content), (
        "src/workflows.ts must include patched('add-notify-customer')."
    )


def test_workflows_complete(start_agent_worker):
    async def _run():
        # Start the NEW workflow execution against the running agent worker.
        await _start_new_workflow()
        # Both old (already started before agent worker) and new must complete.
        old_status = await _wait_for_completed(OLD_WF_ID, timeout_s=180)
        new_status = await _wait_for_completed(NEW_WF_ID, timeout_s=180)
        return old_status, new_status

    old_status, new_status = asyncio.run(_run())
    assert old_status == "COMPLETED", f"Old workflow status: {old_status}"
    assert new_status == "COMPLETED", f"New workflow status: {new_status}"


def test_notify_log_contains_only_new(start_agent_worker):
    # Give activities a moment to flush their writes.
    time.sleep(2)
    assert os.path.isfile(NOTIFY_LOG), f"Expected {NOTIFY_LOG} to exist after run."
    with open(NOTIFY_LOG) as f:
        content = f.read()
    assert f"notified:{NEW_WF_ID}" in content, (
        f"Expected {NOTIFY_LOG} to contain 'notified:{NEW_WF_ID}'. Got:\n{content}"
    )
    assert f"notified:{OLD_WF_ID}" not in content, (
        f"Expected {NOTIFY_LOG} NOT to contain 'notified:{OLD_WF_ID}'. Got:\n{content}"
    )


def test_order_log_contains_both(start_agent_worker):
    time.sleep(2)
    assert os.path.isfile(ORDER_LOG), f"Expected {ORDER_LOG} to exist after run."
    with open(ORDER_LOG) as f:
        content = f.read()
    for expected in (
        f"charged:{OLD_WF_ID}",
        f"shipped:{OLD_WF_ID}",
        f"charged:{NEW_WF_ID}",
        f"shipped:{NEW_WF_ID}",
    ):
        assert expected in content, (
            f"Expected {ORDER_LOG} to contain '{expected}'. Got:\n{content}"
        )
