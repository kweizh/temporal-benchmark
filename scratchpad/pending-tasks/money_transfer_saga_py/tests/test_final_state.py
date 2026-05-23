import asyncio
import json
import os
import re
import subprocess
import sys

import pytest

PROJECT_DIR = "/home/user/myproject"
ACCOUNTS_FILE = "/workspace/accounts.json"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
RUN_ENTRYPOINT = os.path.join(PROJECT_DIR, "run.py")


def _run_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID")
    assert rid, "ZEALT_RUN_ID env var must be set for verification."
    return rid


@pytest.fixture(scope="session")
def run_task():
    """Execute the agent's task entrypoint once, then verify side effects."""
    assert os.path.isfile(RUN_ENTRYPOINT), (
        f"Expected agent to create entrypoint at {RUN_ENTRYPOINT}"
    )
    env = os.environ.copy()
    result = subprocess.run(
        [sys.executable, RUN_ENTRYPOINT],
        cwd=PROJECT_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=300,
    )
    return result


def test_run_entrypoint_executes_successfully(run_task):
    assert run_task.returncode == 0, (
        f"Entrypoint `python3 {RUN_ENTRYPOINT}` must exit with code 0. "
        f"stdout=\n{run_task.stdout}\nstderr=\n{run_task.stderr}"
    )


def test_accounts_json_exists_and_balances_correct(run_task):
    assert os.path.isfile(ACCOUNTS_FILE), (
        f"Expected final state file at {ACCOUNTS_FILE}."
    )
    with open(ACCOUNTS_FILE) as f:
        data = json.load(f)
    assert isinstance(data, dict), (
        f"{ACCOUNTS_FILE} must be a JSON object, got {type(data).__name__}."
    )
    assert data.get("A") == 70, (
        f"Account A final balance must be 70, got {data.get('A')!r}. Full state: {data}"
    )
    assert data.get("B") == 30, (
        f"Account B final balance must be 30, got {data.get('B')!r}. Full state: {data}"
    )
    if "B_FAIL" in data:
        assert data["B_FAIL"] == 0, (
            f"If B_FAIL is present it must equal 0, got {data['B_FAIL']!r}. "
            f"Full state: {data}"
        )


def test_log_file_contains_workflow_ids(run_task):
    rid = _run_id()
    assert os.path.isfile(LOG_FILE), f"Expected log file at {LOG_FILE}."
    with open(LOG_FILE) as f:
        text = f.read()
    ok_pattern = re.compile(rf"OK_WORKFLOW_ID:\s*saga-ok-py-{re.escape(rid)}")
    fail_pattern = re.compile(rf"FAIL_WORKFLOW_ID:\s*saga-fail-py-{re.escape(rid)}")
    assert ok_pattern.search(text), (
        f"Log file {LOG_FILE} must contain 'OK_WORKFLOW_ID: saga-ok-py-{rid}'. "
        f"Got:\n{text}"
    )
    assert fail_pattern.search(text), (
        f"Log file {LOG_FILE} must contain 'FAIL_WORKFLOW_ID: saga-fail-py-{rid}'. "
        f"Got:\n{text}"
    )


def _describe_workflow(workflow_id: str):
    from temporalio.client import Client

    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]

    async def _do():
        client = await Client.connect(
            address,
            namespace=namespace,
            api_key=api_key,
            tls=True,
        )
        handle = client.get_workflow_handle(workflow_id)
        return await handle.describe()

    return asyncio.run(_do())


def test_first_workflow_completed(run_task):
    from temporalio.client import WorkflowExecutionStatus

    rid = _run_id()
    desc = _describe_workflow(f"saga-ok-py-{rid}")
    assert desc.status == WorkflowExecutionStatus.COMPLETED, (
        f"Workflow saga-ok-py-{rid} must be COMPLETED, got status={desc.status!r}."
    )


def test_second_workflow_failed(run_task):
    from temporalio.client import WorkflowExecutionStatus

    rid = _run_id()
    desc = _describe_workflow(f"saga-fail-py-{rid}")
    assert desc.status == WorkflowExecutionStatus.FAILED, (
        f"Workflow saga-fail-py-{rid} must be FAILED, got status={desc.status!r}."
    )
