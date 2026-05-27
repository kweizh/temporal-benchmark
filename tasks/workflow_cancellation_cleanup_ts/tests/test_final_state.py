import asyncio
import os
import subprocess
from datetime import datetime, timedelta, timezone

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
EXPECTED_LOG = "cleanup-done observed"


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", (
        f"Environment variable {name} must be set for the verifier."
    )
    return value


@pytest.fixture(scope="module")
def npm_start_output() -> subprocess.CompletedProcess:
    """Run `npm start` once and reuse its output across tests."""
    env = os.environ.copy()
    result = subprocess.run(
        ["npm", "start"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    return result


def test_npm_start_exits_cleanly(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "`npm start` did not exit with status 0 even though the workflow was "
        "expected to end as CANCELED. "
        f"stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
    )


def test_npm_start_prints_cleanup_done_observed(
    npm_start_output: subprocess.CompletedProcess,
):
    combined = (npm_start_output.stdout or "") + (npm_start_output.stderr or "")
    assert EXPECTED_LOG in combined, (
        f"Expected combined output of `npm start` to contain '{EXPECTED_LOG}', "
        f"got stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
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

    workflow_id_prefix = f"cancel-wf-{run_id}"
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    query = (
        "WorkflowType = 'CancellableWorkflow' "
        f"AND WorkflowId STARTS_WITH '{workflow_id_prefix}' "
        f"AND StartTime > '{cutoff_str}'"
    )

    matches = []
    async for execution in client.list_workflows(query=query):
        matches.append(execution)

    assert matches, (
        "No CancellableWorkflow execution found in Temporal Cloud namespace "
        f"'{namespace}' with WorkflowId prefix '{workflow_id_prefix}' in the last "
        "10 minutes. The agent's `npm start` must have started the workflow."
    )

    matches.sort(
        key=lambda e: e.start_time
        or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    latest = matches[0]

    # Use describe() for strong-consistency status reading.
    handle = client.get_workflow_handle(latest.id, run_id=latest.run_id)
    desc = await handle.describe()
    assert desc.status == WorkflowExecutionStatus.CANCELED, (
        f"Latest matching workflow execution (id={latest.id}, run_id={latest.run_id}) "
        f"is not CANCELED on Temporal Cloud; status={desc.status!r}."
    )
    assert desc.task_queue == "cancel-cleanup-ts", (
        f"Expected workflow task queue 'cancel-cleanup-ts', "
        f"got {desc.task_queue!r}."
    )

    history = await handle.fetch_history()

    # Build a map from scheduled event id -> activity type name so we can
    # correlate ActivityTaskCompleted events back to their activity type.
    scheduled_id_to_activity_type = {}
    for event in history.events:
        # 10 == EVENT_TYPE_ACTIVITY_TASK_SCHEDULED
        if int(event.event_type) == 10:
            attrs = event.activity_task_scheduled_event_attributes
            scheduled_id_to_activity_type[event.event_id] = attrs.activity_type.name

    completed_activity_types = []
    for event in history.events:
        # 11 == EVENT_TYPE_ACTIVITY_TASK_COMPLETED
        if int(event.event_type) == 11:
            attrs = event.activity_task_completed_event_attributes
            scheduled_event_id = attrs.scheduled_event_id
            activity_type = scheduled_id_to_activity_type.get(scheduled_event_id)
            if activity_type:
                completed_activity_types.append(activity_type)

    assert "cleanup" in completed_activity_types, (
        "Expected workflow history to contain an ActivityTaskCompleted event "
        "for activity type 'cleanup'. "
        f"Found completed activities: {completed_activity_types!r}."
    )


def test_workflow_canceled_and_cleanup_completed_in_cloud(
    npm_start_output: subprocess.CompletedProcess,
):
    assert npm_start_output.returncode == 0, (
        "Skipping cloud verification because `npm start` did not exit cleanly."
    )
    asyncio.run(_verify_workflow_in_cloud())
