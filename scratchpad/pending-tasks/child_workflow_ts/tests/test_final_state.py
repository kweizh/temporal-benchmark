import asyncio
import os
import subprocess
from datetime import datetime, timedelta, timezone

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
CLIENT_INPUT = [1, 2, 3]
EXPECTED_RESULT = sum(n * 2 for n in CLIENT_INPUT)  # 12


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


def test_npm_start_prints_expected_result(npm_start_output: subprocess.CompletedProcess):
    combined = (npm_start_output.stdout or "") + (npm_start_output.stderr or "")
    assert str(EXPECTED_RESULT) in combined, (
        f"Expected combined output of `npm start` to contain '{EXPECTED_RESULT}' "
        f"(the sum of doubled values for input {CLIENT_INPUT}), "
        f"got stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
    )


async def _verify_workflows_in_cloud() -> None:
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

    parent_id_prefix = f"parent-wf-{run_id}"
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    # 1) Find the parent workflow execution.
    parent_query = (
        "WorkflowType = 'ParentSumWorkflow' "
        f"AND WorkflowId STARTS_WITH '{parent_id_prefix}' "
        f"AND StartTime > '{cutoff_str}'"
    )

    parents = []
    async for execution in client.list_workflows(query=parent_query):
        parents.append(execution)

    assert parents, (
        "No ParentSumWorkflow execution found in Temporal Cloud namespace "
        f"'{namespace}' with WorkflowId prefix '{parent_id_prefix}' in the last "
        "10 minutes. The agent's `npm start` must have started and completed the "
        "parent workflow."
    )

    parents.sort(
        key=lambda e: e.start_time or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )
    latest_parent = parents[0]

    assert latest_parent.status == WorkflowExecutionStatus.COMPLETED, (
        f"Latest matching parent workflow execution (id={latest_parent.id}, "
        f"run_id={latest_parent.run_id}) is not COMPLETED. "
        f"status={latest_parent.status}"
    )

    handle = client.get_workflow_handle(latest_parent.id, run_id=latest_parent.run_id)
    result = await handle.result()
    assert result == EXPECTED_RESULT, (
        f"Expected parent workflow result to equal {EXPECTED_RESULT} "
        f"(sum of doubled values for input {CLIENT_INPUT}), got: {result!r}"
    )

    # 2) Confirm at least one DoubleWorkflow child execution exists in the window.
    child_query = (
        "WorkflowType = 'DoubleWorkflow' "
        f"AND StartTime > '{cutoff_str}'"
    )

    children = []
    async for execution in client.list_workflows(query=child_query):
        children.append(execution)

    assert children, (
        "No DoubleWorkflow child executions were found in Temporal Cloud "
        f"namespace '{namespace}' in the last 10 minutes. The parent workflow "
        "must invoke DoubleWorkflow via executeChild for each input element."
    )


def test_workflows_completed_in_temporal_cloud(
    npm_start_output: subprocess.CompletedProcess,
):
    # Ensure the agent's start command actually ran before querying.
    assert npm_start_output.returncode == 0, (
        "Skipping cloud verification because `npm start` did not exit cleanly."
    )
    asyncio.run(_verify_workflows_in_cloud())
