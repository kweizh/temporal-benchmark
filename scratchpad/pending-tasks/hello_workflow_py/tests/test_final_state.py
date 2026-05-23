import asyncio
import os
import subprocess
from datetime import datetime, timedelta, timezone

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
EXPECTED_GREETING = "Hello, Temporal!"


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", \
        f"Environment variable {name} must be set for the verifier."
    return value


@pytest.fixture(scope="module")
def run_sh_output() -> subprocess.CompletedProcess:
    """Run `bash run.sh` once and reuse its output across tests."""
    env = os.environ.copy()
    result = subprocess.run(
        ["bash", "run.sh"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    return result


def test_run_sh_succeeds(run_sh_output: subprocess.CompletedProcess):
    assert run_sh_output.returncode == 0, (
        "`bash run.sh` did not exit successfully. "
        f"stdout=\n{run_sh_output.stdout}\nstderr=\n{run_sh_output.stderr}"
    )


def test_run_sh_prints_greeting(run_sh_output: subprocess.CompletedProcess):
    combined = (run_sh_output.stdout or "") + (run_sh_output.stderr or "")
    assert EXPECTED_GREETING in combined, (
        f"Expected combined output of `bash run.sh` to contain '{EXPECTED_GREETING}', "
        f"got stdout=\n{run_sh_output.stdout}\nstderr=\n{run_sh_output.stderr}"
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

    workflow_id_prefix = f"hello-py-{run_id}"
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=10)
    cutoff_str = cutoff.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    query = (
        "WorkflowType = 'HelloWorkflow' "
        f"AND WorkflowId STARTS_WITH '{workflow_id_prefix}' "
        f"AND StartTime > '{cutoff_str}'"
    )

    matches = []
    async for execution in client.list_workflows(query=query):
        matches.append(execution)

    assert matches, (
        "No matching HelloWorkflow execution found in Temporal Cloud namespace "
        f"'{namespace}' with WorkflowId prefix '{workflow_id_prefix}' in the last "
        "10 minutes. The agent's `bash run.sh` must have started and completed the "
        "workflow."
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

    handle = client.get_workflow_handle(latest.id, run_id=latest.run_id)
    result = await handle.result()
    assert result == EXPECTED_GREETING, (
        f"Expected workflow result to equal '{EXPECTED_GREETING}', got: {result!r}"
    )


def test_workflow_completed_in_temporal_cloud(run_sh_output: subprocess.CompletedProcess):
    # Ensure the agent's start command actually ran before querying.
    assert run_sh_output.returncode == 0, (
        "Skipping cloud verification because `bash run.sh` did not exit cleanly."
    )
    asyncio.run(_verify_workflow_in_cloud())
