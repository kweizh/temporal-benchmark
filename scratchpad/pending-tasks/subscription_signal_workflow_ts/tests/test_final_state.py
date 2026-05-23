import asyncio
import json
import os
import re
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = "/workspace/charges.log"
FINAL_RESULT_RE = re.compile(r"Final result:\s*(\{.*\})")


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", (
        f"Environment variable {name} must be set for the verifier."
    )
    return value


@pytest.fixture(scope="module")
def npm_start_output() -> subprocess.CompletedProcess:
    """Run `npm start` once and reuse its output across tests.

    Clean up the log file beforehand so the test only sees the charges
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
def client_final_result(npm_start_output: subprocess.CompletedProcess) -> dict:
    """Parse the JSON object printed by the client after the workflow finishes."""
    combined = (npm_start_output.stdout or "") + "\n" + (npm_start_output.stderr or "")
    match = FINAL_RESULT_RE.search(combined)
    assert match is not None, (
        "Expected stdout/stderr of `npm start` to contain a line in the form "
        "`Final result: <json>`. Got:\n"
        f"stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
    )
    raw = match.group(1)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:
        pytest.fail(
            f"Could not parse JSON from `Final result:` line: {raw!r} ({exc})"
        )


def test_npm_start_succeeds(npm_start_output: subprocess.CompletedProcess):
    assert npm_start_output.returncode == 0, (
        "`npm start` did not exit successfully. "
        f"stdout=\n{npm_start_output.stdout}\nstderr=\n{npm_start_output.stderr}"
    )


def test_client_final_result_shape(client_final_result: dict):
    assert isinstance(client_final_result, dict), (
        f"Expected the workflow's final result to be a JSON object, "
        f"got: {client_final_result!r}"
    )
    assert client_final_result.get("cancelled") is True, (
        "Expected `cancelled` to be true in the workflow's final result, "
        f"got: {client_final_result!r}"
    )
    assert client_final_result.get("finalTier") == "premium", (
        "Expected `finalTier` to be 'premium' after upgrade signal, "
        f"got: {client_final_result!r}"
    )
    billings = client_final_result.get("billings")
    assert isinstance(billings, int) and billings >= 1, (
        f"Expected `billings` to be an integer >= 1, got: {billings!r}"
    )


def test_charges_log_contains_premium_charge(
    npm_start_output: subprocess.CompletedProcess,
):
    assert npm_start_output.returncode == 0, (
        "Skipping log-file check because `npm start` did not exit cleanly."
    )
    assert os.path.isfile(LOG_FILE), (
        f"Expected the chargeCard activity to create the log file at {LOG_FILE}, "
        "but it does not exist."
    )
    with open(LOG_FILE, "r") as fh:
        lines = [line.rstrip("\n") for line in fh.readlines() if line.strip() != ""]
    assert len(lines) >= 1, (
        f"Expected at least one charge line in {LOG_FILE}, got: {lines!r}"
    )
    line_pattern = re.compile(r"^[^:\s]+:[^:\s]+$")
    for line in lines:
        assert line_pattern.match(line), (
            f"Charge log line {line!r} does not match the expected "
            "<userId>:<tier> format."
        )
    assert "u1:premium" in lines, (
        f"Expected at least one `u1:premium` line in {LOG_FILE}, got: {lines!r}"
    )


async def _fetch_cloud_workflow_result() -> dict:
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

    workflow_id = f"sub-{run_id}"
    handle = client.get_workflow_handle(workflow_id)

    description = await handle.describe()
    assert description.status == WorkflowExecutionStatus.COMPLETED, (
        f"Workflow execution (id={workflow_id}) is not COMPLETED. "
        f"status={description.status}"
    )

    return await handle.result()


def test_workflow_completed_in_temporal_cloud(
    npm_start_output: subprocess.CompletedProcess,
    client_final_result: dict,
):
    assert npm_start_output.returncode == 0, (
        "Skipping cloud verification because `npm start` did not exit cleanly."
    )
    cloud_result = asyncio.run(_fetch_cloud_workflow_result())

    assert isinstance(cloud_result, dict), (
        f"Expected workflow result from Temporal Cloud to be a JSON object, "
        f"got: {cloud_result!r}"
    )
    assert cloud_result.get("cancelled") is True, (
        f"Expected Temporal Cloud workflow result `cancelled` to be true, "
        f"got: {cloud_result!r}"
    )
    assert cloud_result.get("finalTier") == "premium", (
        f"Expected Temporal Cloud workflow result `finalTier` == 'premium', "
        f"got: {cloud_result!r}"
    )
    cloud_billings = cloud_result.get("billings")
    assert isinstance(cloud_billings, int) and cloud_billings >= 1, (
        f"Expected Temporal Cloud workflow result `billings` to be an integer >= 1, "
        f"got: {cloud_billings!r}"
    )

    # Client-printed and cloud-returned values must agree.
    assert cloud_result.get("finalTier") == client_final_result.get("finalTier"), (
        "Client-printed finalTier and Temporal Cloud finalTier disagree: "
        f"client={client_final_result!r}, cloud={cloud_result!r}"
    )
    assert cloud_result.get("billings") == client_final_result.get("billings"), (
        "Client-printed billings and Temporal Cloud billings disagree: "
        f"client={client_final_result!r}, cloud={cloud_result!r}"
    )
