import asyncio
import json
import os
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
ACCOUNTS_FILE = "/workspace/accounts.json"
INITIAL_ACCOUNTS = {"A": 100, "B": 0}


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", \
        f"Environment variable {name} must be set for the verifier."
    return value


@pytest.fixture(scope="module")
def npm_start_output() -> subprocess.CompletedProcess:
    """Reset the shared accounts file, run `npm start` once, reuse its output."""
    os.makedirs("/workspace", exist_ok=True)
    with open(ACCOUNTS_FILE, "w") as fh:
        json.dump(INITIAL_ACCOUNTS, fh)

    env = os.environ.copy()
    result = subprocess.run(
        ["npm", "start"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=600,
    )
    return result


def test_npm_start_succeeds(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "`npm start` did not exit successfully. "
        f"stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
    )


def test_accounts_file_final_state(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "Skipping accounts file check because `npm start` did not exit cleanly."
    )
    assert os.path.isfile(ACCOUNTS_FILE), (
        f"Expected the accounts file {ACCOUNTS_FILE} to still exist after the saga ran."
    )
    with open(ACCOUNTS_FILE, "r") as fh:
        data = json.load(fh)
    assert isinstance(data, dict), (
        f"Expected {ACCOUNTS_FILE} to contain a JSON object, got: {data!r}"
    )

    # Account A: started at 100, withdrew 30 for the successful transfer,
    # withdrew 50 for the failing transfer but was refunded — net -30 => 70.
    assert data.get("A") == 70, (
        f"Expected balance A == 70 (initial 100 - successful 30 transfer; "
        f"failing 50 was fully refunded). Got accounts.json = {data!r}"
    )
    # Account B: received the successful 30-unit deposit.
    assert data.get("B") == 30, (
        f"Expected balance B == 30 (received the 30-unit successful deposit). "
        f"Got accounts.json = {data!r}"
    )
    # B_FAIL: the failing deposit must never have credited it. The agent may
    # either omit this key or set it to 0. Accept both: a missing key is 0.
    b_fail = data.get("B_FAIL", 0)
    assert b_fail == 0, (
        f"Expected balance B_FAIL == 0 (the failing deposit must never have "
        f"credited B_FAIL). Got accounts.json = {data!r}"
    )


async def _verify_workflows_in_cloud():
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

    ok_workflow_id = f"saga-ok-{run_id}"
    fail_workflow_id = f"saga-fail-{run_id}"

    ok_handle = client.get_workflow_handle(ok_workflow_id)
    ok_desc = await ok_handle.describe()
    assert ok_desc.status == WorkflowExecutionStatus.COMPLETED, (
        f"Workflow execution (id={ok_workflow_id}) is not COMPLETED. "
        f"status={ok_desc.status}"
    )

    fail_handle = client.get_workflow_handle(fail_workflow_id)
    fail_desc = await fail_handle.describe()
    assert fail_desc.status == WorkflowExecutionStatus.FAILED, (
        f"Workflow execution (id={fail_workflow_id}) is not FAILED. "
        f"Expected FAILED so the saga propagated the failure after running its "
        f"compensation. status={fail_desc.status}"
    )

    # Confirm the compensation `refund` activity actually ran in the failing
    # workflow by walking history events.
    refund_seen = False
    async for event in fail_handle.fetch_history_events():
        attrs = getattr(event, "activity_task_scheduled_event_attributes", None)
        if attrs is not None and getattr(attrs, "activity_type", None) is not None:
            name = getattr(attrs.activity_type, "name", "")
            if name == "refund":
                refund_seen = True
                break
    assert refund_seen, (
        f"Expected the failing workflow {fail_workflow_id} to have scheduled "
        "a `refund` activity for saga compensation, but no such event was "
        "found in history."
    )


def test_workflows_in_temporal_cloud(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "Skipping cloud verification because `npm start` did not exit cleanly."
    )
    asyncio.run(_verify_workflows_in_cloud())
