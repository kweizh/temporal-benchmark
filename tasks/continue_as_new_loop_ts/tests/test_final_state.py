import asyncio
import os
import re
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
WORKFLOW_FILE = os.path.join(PROJECT_DIR, "src", "workflows.ts")
LOG_FILE = "/workspace/loop.log"
FINAL_RESULT_RE = re.compile(r"Final result:\s*(\d+)")


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", (
        f"Environment variable {name} must be set for the verifier."
    )
    return value


@pytest.fixture(scope="module")
def npm_start_output() -> subprocess.CompletedProcess:
    """Run `npm start` once and reuse its output across tests.

    Clean up the log file beforehand so the test only sees the lines
    produced by this verification run.
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


@pytest.fixture(scope="module")
def client_final_result(npm_start_output: subprocess.CompletedProcess) -> int:
    """Parse the integer printed by the client after the workflow finishes."""
    combined = (npm_start_output.stdout or "") + "\n" + (npm_start_output.stderr or "")
    match = FINAL_RESULT_RE.search(combined)
    assert match is not None, (
        "Expected stdout/stderr of `npm start` to contain a line in the form "
        "`Final result: <integer>`. Got:\n"
        f"stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
    )
    return int(match.group(1))


def test_npm_start_succeeds(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "`npm start` did not exit successfully. "
        f"stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
    )


def test_client_prints_final_result_25(client_final_result: int):
    assert client_final_result == 25, (
        f"Expected client to print `Final result: 25`, got: {client_final_result}"
    )


def test_loop_log_contains_exact_25_lines(
    npm_start_output: subprocess.CompletedProcess,
):
    assert npm_start_output.returncode == 0, (
        "Skipping log-file check because `npm start` did not exit cleanly."
    )
    assert os.path.isfile(LOG_FILE), (
        f"Expected the incrementCounter activity to create the log file at "
        f"{LOG_FILE}, but it does not exist."
    )
    with open(LOG_FILE, "r") as fh:
        raw_lines = fh.readlines()
    lines = [line.strip() for line in raw_lines if line.strip() != ""]
    assert len(lines) == 25, (
        f"Expected exactly 25 non-empty lines in {LOG_FILE}, got {len(lines)}: "
        f"{lines!r}"
    )
    expected = [str(i) for i in range(1, 26)]
    assert lines == expected, (
        "Expected loop.log to contain the integers 1..25 in order, one per line. "
        f"Got: {lines!r}"
    )


def test_workflow_source_uses_continue_as_new():
    assert os.path.isfile(WORKFLOW_FILE), (
        f"Workflow source file {WORKFLOW_FILE} must exist."
    )
    with open(WORKFLOW_FILE, "r") as fh:
        source = fh.read()
    assert re.search(r"continueAsNew\(", source), (
        "Expected the workflow source at "
        f"{WORKFLOW_FILE} to call `continueAsNew(...)`. Source was:\n{source}"
    )


async def _fetch_chain_and_final_result():
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

    workflow_id = f"loop-{run_id}"

    # Latest run handle.
    handle = client.get_workflow_handle(workflow_id)
    description = await handle.describe()
    final_result = await handle.result()

    # Enumerate all runs in the chain by listing workflows with this id.
    query = f"WorkflowId = '{workflow_id}'"
    executions = []
    async for execution in client.list_workflows(query=query):
        executions.append(execution)

    return workflow_id, description, final_result, executions


def test_workflow_chain_in_temporal_cloud(
    npm_start_output: subprocess.CompletedProcess,
    client_final_result: int,
):
    assert npm_start_output.returncode == 0, (
        "Skipping cloud verification because `npm start` did not exit cleanly."
    )
    workflow_id, description, final_result, executions = asyncio.run(
        _fetch_chain_and_final_result()
    )

    assert description.status == WorkflowExecutionStatus.COMPLETED, (
        f"Latest run of workflow id={workflow_id} is not COMPLETED. "
        f"status={description.status}"
    )

    assert final_result == 25, (
        f"Expected Temporal Cloud workflow result to be 25, got: {final_result!r}"
    )
    assert final_result == client_final_result, (
        "Client-printed final result and Temporal Cloud final result disagree: "
        f"client={client_final_result}, cloud={final_result}"
    )

    # Enumerate the chain of run ids for this workflow id.
    assert len(executions) > 0, (
        f"Expected at least one execution for workflow id={workflow_id}, "
        f"got none."
    )

    run_ids = {e.run_id for e in executions}
    assert len(run_ids) >= 3, (
        "Expected the continue-as-new chain to contain at least 3 distinct "
        f"run ids (original + at least 2 continued runs), got "
        f"{len(run_ids)}: {run_ids!r}"
    )

    completed_count = sum(
        1 for e in executions if e.status == WorkflowExecutionStatus.COMPLETED
    )
    continued_count = sum(
        1
        for e in executions
        if e.status == WorkflowExecutionStatus.CONTINUED_AS_NEW
    )
    assert completed_count == 1, (
        "Expected exactly one COMPLETED run in the chain (the final one), got "
        f"{completed_count}. Statuses: {[e.status for e in executions]!r}"
    )
    assert continued_count >= 2, (
        "Expected at least 2 CONTINUED_AS_NEW runs in the chain, got "
        f"{continued_count}. Statuses: {[e.status for e in executions]!r}"
    )
