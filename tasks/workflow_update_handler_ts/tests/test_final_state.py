import asyncio
import os
import re
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"

EXPECTED_LINES = [
    "Updated balance: 100",
    "Updated balance: 150",
    "Updated balance: 175",
    "Final balance: 175",
]


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


def test_npm_start_succeeds(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "`npm start` did not exit successfully. "
        f"stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
    )


def test_npm_start_prints_expected_lines_in_order(
    npm_start_output: subprocess.CompletedProcess,
):
    combined = (npm_start_output.stdout or "") + "\n" + (npm_start_output.stderr or "")
    # Use a regex anchored to line boundaries to confirm each expected line
    # appears at least once on its own line, and that the expected lines appear
    # in the required order.
    last_index = -1
    for expected in EXPECTED_LINES:
        pattern = re.compile(r"^\s*" + re.escape(expected) + r"\s*$", re.MULTILINE)
        match = pattern.search(combined, last_index + 1 if last_index >= 0 else 0)
        assert match is not None, (
            f"Expected `npm start` output to contain a line equal to "
            f"{expected!r}. Got:\n"
            f"stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
        )
        assert match.start() > last_index, (
            f"Expected line {expected!r} to appear after the previously matched "
            f"expected line in `npm start` output. Got:\n"
            f"stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
        )
        last_index = match.start()


async def _fetch_cloud_workflow_result():
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

    workflow_id = f"update-wf-{run_id}"
    handle = client.get_workflow_handle(workflow_id)

    description = await handle.describe()
    assert description.status == WorkflowExecutionStatus.COMPLETED, (
        f"Workflow execution (id={workflow_id}) is not COMPLETED. "
        f"status={description.status}"
    )

    return await handle.result()


def test_workflow_completed_in_temporal_cloud(
    npm_start_output: subprocess.CompletedProcess,
):
    assert npm_start_output.returncode == 0, (
        "Skipping cloud verification because `npm start` did not exit cleanly."
    )
    cloud_result = asyncio.run(_fetch_cloud_workflow_result())
    assert cloud_result == 175, (
        f"Expected Temporal Cloud workflow result to equal 175, got: {cloud_result!r}"
    )
