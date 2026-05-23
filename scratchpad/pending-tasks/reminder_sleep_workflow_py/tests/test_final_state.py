import asyncio
import os
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = "/workspace/reminder.log"
EXPECTED_RESULT = "Notified: wake up"


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", \
        f"Environment variable {name} must be set for the verifier."
    return value


@pytest.fixture(scope="module")
def run_sh_output() -> subprocess.CompletedProcess:
    """Run `bash run.sh` once and reuse its output across tests."""
    # Clean up the log file before the run so the verifier asserts a fresh file.
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

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


def test_run_sh_prints_expected_result(run_sh_output: subprocess.CompletedProcess):
    combined = (run_sh_output.stdout or "") + (run_sh_output.stderr or "")
    assert EXPECTED_RESULT in combined, (
        f"Expected combined output of `bash run.sh` to contain '{EXPECTED_RESULT}', "
        f"got stdout=\n{run_sh_output.stdout}\nstderr=\n{run_sh_output.stderr}"
    )


def test_reminder_log_file_contains_notification(run_sh_output: subprocess.CompletedProcess):
    assert run_sh_output.returncode == 0, (
        "Skipping log file check because `bash run.sh` did not exit cleanly."
    )
    assert os.path.isfile(LOG_FILE), \
        f"Expected log file {LOG_FILE} to exist after the workflow runs."
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = [line.rstrip("\n") for line in f.readlines()]
    assert EXPECTED_RESULT in lines, (
        f"Expected {LOG_FILE} to contain a line equal to '{EXPECTED_RESULT}', "
        f"got lines: {lines!r}"
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

    workflow_id = f"reminder-py-{run_id}"
    handle = client.get_workflow_handle(workflow_id)

    description = await handle.describe()
    assert description.status == WorkflowExecutionStatus.COMPLETED, (
        f"Expected workflow execution {workflow_id} to be COMPLETED, "
        f"got status={description.status}"
    )

    result = await handle.result()
    assert result == EXPECTED_RESULT, (
        f"Expected workflow result to equal '{EXPECTED_RESULT}', got: {result!r}"
    )


def test_workflow_completed_in_temporal_cloud(run_sh_output: subprocess.CompletedProcess):
    assert run_sh_output.returncode == 0, (
        "Skipping cloud verification because `bash run.sh` did not exit cleanly."
    )
    asyncio.run(_verify_workflow_in_cloud())
