import asyncio
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
EXPECTED_RESULT = 10


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


def test_npm_start_prints_final_counter(npm_start_output: subprocess.CompletedProcess):
    combined = (npm_start_output.stdout or "") + (npm_start_output.stderr or "")
    # The client must print the final counter value (10) to stdout.
    assert re.search(r"(?<!\d)10(?!\d)", combined), (
        f"Expected combined output of `npm start` to contain the final counter value '10', "
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

    workflow_id_prefix = f"counter-wf-{run_id}"
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    query = (
        "WorkflowType = 'CounterWorkflow' "
        f"AND WorkflowId STARTS_WITH '{workflow_id_prefix}' "
        f"AND StartTime > '{cutoff_str}'"
    )

    matches = []
    async for execution in client.list_workflows(query=query):
        matches.append(execution)

    assert matches, (
        "No CounterWorkflow execution found in Temporal Cloud namespace "
        f"'{namespace}' with WorkflowId prefix '{workflow_id_prefix}' in the last "
        "10 minutes. The agent's `npm start` must have started the workflow."
    )

    matches.sort(
        key=lambda e: e.start_time or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    latest = matches[0]

    assert latest.status == WorkflowExecutionStatus.COMPLETED, (
        f"Latest matching workflow execution (id={latest.id}, run_id={latest.run_id}) "
        f"is not COMPLETED. status={latest.status}"
    )

    assert latest.task_queue == "counter-ts", (
        f"Expected task queue 'counter-ts' for latest CounterWorkflow execution "
        f"(id={latest.id}), got {latest.task_queue!r}."
    )

    handle = client.get_workflow_handle(latest.id, run_id=latest.run_id)
    result = await handle.result()
    assert result == EXPECTED_RESULT, (
        f"Expected workflow result to equal {EXPECTED_RESULT} (5+3+2), got: {result!r}"
    )


def test_workflow_completed_in_temporal_cloud(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "Skipping cloud verification because `npm start` did not exit cleanly."
    )
    asyncio.run(_verify_workflow_in_cloud())
