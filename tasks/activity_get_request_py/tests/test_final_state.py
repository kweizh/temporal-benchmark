import asyncio
import os
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
EXPECTED_RESULT = "temporalio/temporal"


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", \
        f"Environment variable {name} must be set for the verifier."
    return value


@pytest.fixture(scope="module")
def python_main_output() -> subprocess.CompletedProcess:
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


def test_python_main_succeeds(python_main_output: subprocess.CompletedProcess):
    assert python_main_output.returncode == 0, (
        "`python main.py` did not exit successfully. "
        f"stdout=\n{python_main_output.stdout}\nstderr=\n{python_main_output.stderr}"
    )


def test_python_main_prints_repo_full_name(
    python_main_output: subprocess.CompletedProcess,
):
    combined = (python_main_output.stdout or "") + (python_main_output.stderr or "")
    assert EXPECTED_RESULT in combined, (
        f"Expected combined output of `python main.py` to contain '{EXPECTED_RESULT}', "
        f"got stdout=\n{python_main_output.stdout}\nstderr=\n{python_main_output.stderr}"
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

    workflow_id = f"repo-fetch-py-{run_id}"
    handle = client.get_workflow_handle(workflow_id)

    description = await handle.describe()
    assert description.workflow_type == "FetchRepoWorkflow", (
        f"Expected workflow type 'FetchRepoWorkflow' for workflow id '{workflow_id}', "
        f"got: {description.workflow_type!r}"
    )
    assert description.status == WorkflowExecutionStatus.COMPLETED, (
        f"Expected workflow '{workflow_id}' to have status COMPLETED, "
        f"got: {description.status}"
    )

    result = await handle.result()
    assert result == EXPECTED_RESULT, (
        f"Expected workflow result to equal {EXPECTED_RESULT!r}, got: {result!r}"
    )


def test_workflow_completed_in_temporal_cloud(
    python_main_output: subprocess.CompletedProcess,
):
    # Ensure the agent's start command actually ran before querying.
    assert python_main_output.returncode == 0, (
        "Skipping cloud verification because `python main.py` did not exit cleanly."
    )
    asyncio.run(_verify_workflow_in_cloud())
