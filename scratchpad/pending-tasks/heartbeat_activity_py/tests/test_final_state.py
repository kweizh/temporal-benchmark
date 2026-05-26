import asyncio
import os
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus
from temporalio.api.enums.v1 import EventType

PROJECT_DIR = "/home/user/myproject"
EXPECTED_RESULT = 5


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", \
        f"Environment variable {name} must be set for the verifier."
    return value


@pytest.fixture(scope="module")
def run_output() -> subprocess.CompletedProcess:
    """Run `python main.py` once and reuse its output across tests."""
    env = os.environ.copy()
    result = subprocess.run(
        ["python", "main.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    return result


def test_main_py_succeeds(run_output: subprocess.CompletedProcess):
    assert run_output.returncode == 0, (
        "`python main.py` did not exit successfully. "
        f"stdout=\n{run_output.stdout}\nstderr=\n{run_output.stderr}"
    )


def test_main_py_prints_expected_count(run_output: subprocess.CompletedProcess):
    combined = (run_output.stdout or "") + (run_output.stderr or "")
    assert str(EXPECTED_RESULT) in combined, (
        f"Expected combined output of `python main.py` to contain '{EXPECTED_RESULT}', "
        f"got stdout=\n{run_output.stdout}\nstderr=\n{run_output.stderr}"
    )


async def _verify_workflow_in_cloud() -> None:
    address = _get_env("TEMPORAL_ADDRESS")
    namespace = _get_env("TEMPORAL_NAMESPACE")
    api_key = _get_env("TEMPORAL_API_KEY")
    run_id = _get_env("ZEALT_RUN_ID")

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    workflow_id = f"heartbeat-wf-{run_id}"
    handle = client.get_workflow_handle(workflow_id)

    description = await handle.describe()
    assert description.status == WorkflowExecutionStatus.COMPLETED, (
        f"Expected workflow execution {workflow_id} to be COMPLETED, "
        f"got status={description.status}"
    )

    result = await handle.result()
    assert result == EXPECTED_RESULT, (
        f"Expected workflow result to equal {EXPECTED_RESULT!r}, got: {result!r}"
    )

    # Fetch the full event history for the workflow execution and inspect it.
    history = await handle.fetch_history()
    events = list(history.events)
    event_types = [event.event_type for event in events]

    assert EventType.EVENT_TYPE_ACTIVITY_TASK_STARTED in event_types, (
        f"Expected at least one ActivityTaskStarted event in the history of "
        f"workflow {workflow_id}, got event types: {event_types!r}"
    )

    assert EventType.EVENT_TYPE_ACTIVITY_TASK_TIMED_OUT not in event_types, (
        f"Expected no ActivityTaskTimedOut events in the history of "
        f"workflow {workflow_id}, but one was found. Event types: {event_types!r}"
    )


def test_workflow_completed_in_temporal_cloud(run_output: subprocess.CompletedProcess):
    assert run_output.returncode == 0, (
        "Skipping cloud verification because `python main.py` did not exit cleanly."
    )
    asyncio.run(_verify_workflow_in_cloud())
