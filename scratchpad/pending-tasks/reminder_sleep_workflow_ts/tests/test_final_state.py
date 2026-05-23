import asyncio
import os
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = "/workspace/reminder.log"
EXPECTED_REMINDER = "Notified: wake up"


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", \
        f"Environment variable {name} must be set for the verifier."
    return value


@pytest.fixture(scope="module")
def npm_start_output() -> subprocess.CompletedProcess:
    """Run `npm start` once and reuse its output across tests.

    Clean up the log file beforehand so the test only sees the line produced
    by this verification run.
    """
    os.makedirs("/workspace", exist_ok=True)
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

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


def test_npm_start_prints_reminder(npm_start_output: subprocess.CompletedProcess):
    combined = (npm_start_output.stdout or "") + (npm_start_output.stderr or "")
    assert EXPECTED_REMINDER in combined, (
        f"Expected combined output of `npm start` to contain '{EXPECTED_REMINDER}', "
        f"got stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
    )


def test_reminder_log_written_by_activity(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "Skipping log-file check because `npm start` did not exit cleanly."
    )
    assert os.path.isfile(LOG_FILE), (
        f"Expected the Notify activity to create the log file at {LOG_FILE}, "
        "but it does not exist."
    )
    with open(LOG_FILE, "r") as fh:
        lines = [line.rstrip("\n") for line in fh.readlines()]
    assert EXPECTED_REMINDER in lines, (
        f"Expected log file {LOG_FILE} to contain a line equal to "
        f"'{EXPECTED_REMINDER}', got lines: {lines!r}"
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

    workflow_id = f"reminder-{run_id}"
    handle = client.get_workflow_handle(workflow_id)

    description = await handle.describe()
    assert description.status == WorkflowExecutionStatus.COMPLETED, (
        f"Workflow execution (id={workflow_id}) is not COMPLETED. "
        f"status={description.status}"
    )

    result = await handle.result()
    assert result == EXPECTED_REMINDER, (
        f"Expected workflow result to equal '{EXPECTED_REMINDER}', got: {result!r}"
    )


def test_workflow_completed_in_temporal_cloud(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "Skipping cloud verification because `npm start` did not exit cleanly."
    )
    asyncio.run(_verify_workflow_in_cloud())
