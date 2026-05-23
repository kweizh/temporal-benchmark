import asyncio
import os
import re

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

ATTEMPTS_LOG = "/workspace/attempts.log"
RESULT_LOG = "/workspace/result.log"
EXPECTED_RESULT = "failed after 5 attempts"
EXPECTED_ATTEMPTS = 5


def _run_id():
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    return run_id


def test_result_log_exists_and_matches():
    assert os.path.isfile(RESULT_LOG), f"{RESULT_LOG} was not created by the task."
    with open(RESULT_LOG) as f:
        content = f.read()
    pattern = r"Workflow result:\s*" + re.escape(EXPECTED_RESULT)
    assert re.search(pattern, content), (
        f"{RESULT_LOG} does not contain a line matching 'Workflow result: "
        f"{EXPECTED_RESULT}'. Content was: {content!r}"
    )


def test_attempts_log_exists_and_has_five_lines():
    assert os.path.isfile(ATTEMPTS_LOG), f"{ATTEMPTS_LOG} was not created by the task."
    with open(ATTEMPTS_LOG) as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    assert len(lines) == EXPECTED_ATTEMPTS, (
        f"Expected exactly {EXPECTED_ATTEMPTS} non-empty lines in {ATTEMPTS_LOG}, "
        f"found {len(lines)}: {lines!r}"
    )


@pytest.mark.asyncio
async def test_workflow_completed_on_temporal_cloud():
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    workflow_id = f"retry-py-{_run_id()}"

    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    handle = client.get_workflow_handle(workflow_id)
    desc = await handle.describe()
    assert desc.status == WorkflowExecutionStatus.COMPLETED, (
        f"Workflow {workflow_id} status is {desc.status!r}, expected COMPLETED."
    )

    result = await handle.result()
    assert result == EXPECTED_RESULT, (
        f"Workflow {workflow_id} returned {result!r}, expected {EXPECTED_RESULT!r}."
    )
