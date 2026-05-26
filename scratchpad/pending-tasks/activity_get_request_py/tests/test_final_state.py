import asyncio
import os
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus


PROJECT_DIR = "/home/user/myproject"


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", \
        f"Environment variable {name} must be set for the verifier."
    return value


@pytest.fixture(scope="module")
def run_output() -> subprocess.CompletedProcess:
    """Run `python3 main.py` once and reuse its output across tests."""
    env = os.environ.copy()
    result = subprocess.run(
        ["python3", "main.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    return result


def test_run_succeeds(run_output: subprocess.CompletedProcess):
    assert run_output.returncode == 0, (
        "`python3 main.py` did not exit successfully. "
        f"stdout=\n{run_output.stdout}\nstderr=\n{run_output.stderr}"
    )


def test_run_prints_non_empty_result(run_output: subprocess.CompletedProcess):
    assert run_output.returncode == 0, (
        "Skipping output check because `python3 main.py` did not exit cleanly."
    )
    combined = (run_output.stdout or "") + (run_output.stderr or "")
    # The GitHub Zen API returns a non-empty single-line quote. The client
    # entrypoint is required to print the workflow result to stdout, so we
    # expect at least one non-empty line in the combined output.
    non_empty_lines = [line for line in combined.splitlines() if line.strip()]
    assert non_empty_lines, (
        "Expected `python3 main.py` to print at least one non-empty line "
        f"(the workflow result). Got stdout=\n{run_output.stdout}\nstderr=\n{run_output.stderr}"
    )


async def _verify_workflow_in_cloud() -> str:
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

    workflow_id = f"fetch-wf-{run_id}"
    handle = client.get_workflow_handle(workflow_id)

    description = await handle.describe()
    assert description.status == WorkflowExecutionStatus.COMPLETED, (
        f"Expected workflow execution {workflow_id} to be COMPLETED, "
        f"got status={description.status}"
    )

    result = await handle.result()
    assert isinstance(result, str), (
        f"Expected workflow result to be a str, got type={type(result).__name__}: {result!r}"
    )
    assert result != "", (
        f"Expected workflow result to be a non-empty string, got empty string."
    )
    return result


def test_workflow_completed_in_temporal_cloud(run_output: subprocess.CompletedProcess):
    assert run_output.returncode == 0, (
        "Skipping cloud verification because `python3 main.py` did not exit cleanly."
    )
    result = asyncio.run(_verify_workflow_in_cloud())
    combined = (run_output.stdout or "") + (run_output.stderr or "")
    # As an integrity check, ensure the workflow result also appears in the
    # client's stdout/stderr output (the client must print the result).
    assert result.strip() in combined, (
        f"Expected the workflow result (from Temporal Cloud) to also appear in "
        f"the client's combined output. "
        f"workflow result={result!r}, combined output=\n{combined}"
    )
