import asyncio
import os
import shutil
import subprocess
import sys
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


def _python_executable() -> str:
    for candidate in ("python", "python3"):
        path = shutil.which(candidate)
        if path:
            return path
    return sys.executable


@pytest.fixture(scope="module")
def main_py_output() -> subprocess.CompletedProcess:
    """Run `python main.py` once and reuse its output across tests."""
    env = os.environ.copy()
    result = subprocess.run(
        [_python_executable(), "main.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    return result


def test_main_py_succeeds(main_py_output: subprocess.CompletedProcess):
    assert main_py_output.returncode == 0, (
        "`python main.py` did not exit successfully. "
        f"stdout=\n{main_py_output.stdout}\nstderr=\n{main_py_output.stderr}"
    )


def test_main_py_prints_greeting(main_py_output: subprocess.CompletedProcess):
    combined = (main_py_output.stdout or "") + (main_py_output.stderr or "")
    assert EXPECTED_GREETING in combined, (
        f"Expected combined output of `python main.py` to contain '{EXPECTED_GREETING}', "
        f"got stdout=\n{main_py_output.stdout}\nstderr=\n{main_py_output.stderr}"
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

    workflow_id_prefix = f"hello-wf-{run_id}"
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
        "No HelloWorkflow execution found in Temporal Cloud namespace "
        f"'{namespace}' with WorkflowId prefix '{workflow_id_prefix}' in the last "
        "10 minutes. The agent's `python main.py` must have started and completed the "
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


def test_workflow_completed_in_temporal_cloud(main_py_output: subprocess.CompletedProcess):
    # Ensure the agent's start command actually ran before querying.
    assert main_py_output.returncode == 0, (
        "Skipping cloud verification because `python main.py` did not exit cleanly."
    )
    asyncio.run(_verify_workflow_in_cloud())
