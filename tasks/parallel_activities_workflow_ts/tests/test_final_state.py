import asyncio
import os
import subprocess
from datetime import datetime, timedelta, timezone

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
EXPECTED_INPUT = [1, 2, 3, 4, 5]
EXPECTED_RESULT = 55  # 1*1 + 2*2 + 3*3 + 4*4 + 5*5
WORKFLOW_TYPE = "ParallelSquaresWorkflow"
ACTIVITY_TYPE = "squareNumber"
WORKFLOW_ID_PREFIX_BASE = "parallel-wf-"


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", \
        f"Environment variable {name} must be set for the verifier."
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


def test_npm_start_succeeds(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "`npm start` did not exit successfully. "
        f"stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
    )


def test_npm_start_prints_expected_sum(
    npm_start_output: subprocess.CompletedProcess,
):
    combined = (npm_start_output.stdout or "") + (npm_start_output.stderr or "")
    assert str(EXPECTED_RESULT) in combined, (
        f"Expected combined output of `npm start` to contain '{EXPECTED_RESULT}', "
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

    workflow_id_prefix = f"{WORKFLOW_ID_PREFIX_BASE}{run_id}"
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    query = (
        f"WorkflowType = '{WORKFLOW_TYPE}' "
        f"AND WorkflowId STARTS_WITH '{workflow_id_prefix}' "
        f"AND StartTime > '{cutoff_str}'"
    )

    matches = []
    async for execution in client.list_workflows(query=query):
        matches.append(execution)

    assert matches, (
        f"No {WORKFLOW_TYPE} execution found in Temporal Cloud namespace "
        f"'{namespace}' with WorkflowId prefix '{workflow_id_prefix}' in the "
        "last 10 minutes. The agent's `npm start` must have started and "
        "completed the workflow."
    )

    matches.sort(
        key=lambda e: e.start_time or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    latest = matches[0]

    assert latest.status == WorkflowExecutionStatus.COMPLETED, (
        f"Latest matching workflow execution (id={latest.id}, "
        f"run_id={latest.run_id}) is not COMPLETED. status={latest.status}"
    )

    handle = client.get_workflow_handle(latest.id, run_id=latest.run_id)
    result = await handle.result()
    assert int(result) == EXPECTED_RESULT, (
        f"Expected workflow result to equal {EXPECTED_RESULT} (sum of squares "
        f"of {EXPECTED_INPUT}), got: {result!r}"
    )

    # Inspect history to confirm fan-out parallelism via Promise.all.
    history = await handle.fetch_history()
    scheduled_times = []
    for event in history.events:
        attrs = getattr(event, "activity_task_scheduled_event_attributes", None)
        if attrs is None:
            continue
        activity_type_name = getattr(
            getattr(attrs, "activity_type", None), "name", ""
        )
        if activity_type_name == ACTIVITY_TYPE:
            scheduled_times.append(event.event_time)

    assert len(scheduled_times) == len(EXPECTED_INPUT), (
        f"Expected exactly {len(EXPECTED_INPUT)} ACTIVITY_TASK_SCHEDULED events "
        f"for activity '{ACTIVITY_TYPE}', got {len(scheduled_times)}."
    )

    epoch_seconds = [t.ToMicroseconds() / 1e6 for t in scheduled_times]
    spread = max(epoch_seconds) - min(epoch_seconds)
    assert spread <= 5.0, (
        f"Expected all {len(EXPECTED_INPUT)} '{ACTIVITY_TYPE}' activities to be "
        f"scheduled in parallel within 5 seconds, observed spread of "
        f"{spread:.3f} seconds across event times: {scheduled_times}."
    )


def test_workflow_completed_in_temporal_cloud(
    npm_start_output: subprocess.CompletedProcess,
):
    assert npm_start_output.returncode == 0, (
        "Skipping cloud verification because `npm start` did not exit cleanly."
    )
    asyncio.run(_verify_workflow_in_cloud())
