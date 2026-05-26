import asyncio
import os
import re
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
MID_PATTERN = re.compile(r"^Mid counter: (\d+)$", re.MULTILINE)
FINAL_PATTERN = re.compile(r"^Final counter: (\d+)$", re.MULTILINE)


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


def _combined_output(proc: subprocess.CompletedProcess) -> str:
    return (proc.stdout or "") + "\n" + (proc.stderr or "")


def test_run_sh_succeeds(run_sh_output: subprocess.CompletedProcess):
    assert run_sh_output.returncode == 0, (
        "`bash run.sh` did not exit successfully. "
        f"stdout=\n{run_sh_output.stdout}\nstderr=\n{run_sh_output.stderr}"
    )


def test_run_sh_prints_mid_counter(run_sh_output: subprocess.CompletedProcess):
    combined = _combined_output(run_sh_output)
    match = MID_PATTERN.search(combined)
    assert match, (
        "Expected combined output of `bash run.sh` to contain a line matching "
        "'^Mid counter: <int>$'. "
        f"stdout=\n{run_sh_output.stdout}\nstderr=\n{run_sh_output.stderr}"
    )
    mid_counter = int(match.group(1))
    assert mid_counter >= 0, (
        f"Mid counter must be a non-negative integer, got: {mid_counter}"
    )


def test_run_sh_prints_final_counter(run_sh_output: subprocess.CompletedProcess):
    combined = _combined_output(run_sh_output)
    match = FINAL_PATTERN.search(combined)
    assert match, (
        "Expected combined output of `bash run.sh` to contain a line matching "
        "'^Final counter: <int>$'. "
        f"stdout=\n{run_sh_output.stdout}\nstderr=\n{run_sh_output.stderr}"
    )
    final_counter = int(match.group(1))
    assert final_counter >= 1, (
        f"Final counter must be a positive integer (>=1), got: {final_counter}"
    )


def test_final_counter_is_not_less_than_mid_counter(
    run_sh_output: subprocess.CompletedProcess,
):
    combined = _combined_output(run_sh_output)
    mid_match = MID_PATTERN.search(combined)
    final_match = FINAL_PATTERN.search(combined)
    assert mid_match and final_match, (
        "Both `Mid counter:` and `Final counter:` lines must be present. "
        f"stdout=\n{run_sh_output.stdout}\nstderr=\n{run_sh_output.stderr}"
    )
    mid_counter = int(mid_match.group(1))
    final_counter = int(final_match.group(1))
    assert final_counter >= mid_counter, (
        f"Final counter ({final_counter}) must be >= mid counter ({mid_counter})."
    )


async def _verify_workflow_in_cloud(expected_final_counter: int) -> None:
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

    workflow_id = f"query-wf-{run_id}"
    handle = client.get_workflow_handle(workflow_id)

    description = await handle.describe()
    assert description.status == WorkflowExecutionStatus.COMPLETED, (
        f"Expected workflow execution {workflow_id} to be COMPLETED, "
        f"got status={description.status}"
    )
    assert description.task_queue == "query-handler-py", (
        f"Expected workflow {workflow_id} to be on task queue 'query-handler-py', "
        f"got: {description.task_queue!r}"
    )

    result = await handle.result()
    assert isinstance(result, int) and not isinstance(result, bool), (
        f"Expected workflow result to be an int, got {type(result).__name__}: {result!r}"
    )
    assert result == expected_final_counter, (
        f"Expected workflow result to equal Final counter printed by run.sh "
        f"({expected_final_counter}); got: {result!r}"
    )

    queried = await handle.query("get_counter")
    assert isinstance(queried, int) and not isinstance(queried, bool), (
        f"Expected `get_counter` query to return an int, got "
        f"{type(queried).__name__}: {queried!r}"
    )
    assert queried == expected_final_counter, (
        f"Expected `get_counter` query on the COMPLETED workflow to equal the "
        f"Final counter printed by run.sh ({expected_final_counter}); got: {queried!r}"
    )


def test_workflow_completed_in_temporal_cloud(
    run_sh_output: subprocess.CompletedProcess,
):
    assert run_sh_output.returncode == 0, (
        "Skipping cloud verification because `bash run.sh` did not exit cleanly."
    )
    combined = _combined_output(run_sh_output)
    final_match = FINAL_PATTERN.search(combined)
    assert final_match, (
        "Cannot verify Cloud workflow result without a `Final counter:` line in output."
    )
    expected_final_counter = int(final_match.group(1))
    asyncio.run(_verify_workflow_in_cloud(expected_final_counter))
