import asyncio
import os
import re

import pytest
from temporalio.client import Client, WorkflowExecutionStatus


PROJECT_DIR = "/home/user/myproject"
WORKFLOWS_FILE = os.path.join(PROJECT_DIR, "src", "workflows.ts")
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
TASK_QUEUE = "discount-ts"
VALID_DISCOUNTS = {0, 5, 10, 15, 20}


def _workflow_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is required for verification."
    return f"discount-{run_id}"


async def _connect() -> Client:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    return await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
        rpc_metadata={"temporal-namespace": namespace},
    )


@pytest.fixture(scope="module")
def workflow_handle():
    async def _run():
        client = await _connect()
        return client, client.get_workflow_handle(_workflow_id())

    return asyncio.run(_run())


def test_workflows_ts_no_math_random():
    assert os.path.isfile(WORKFLOWS_FILE), f"{WORKFLOWS_FILE} does not exist."
    with open(WORKFLOWS_FILE) as f:
        content = f.read()
    assert not re.search(r"Math\.random", content), (
        "src/workflows.ts must NOT contain 'Math.random' after the fix."
    )


def test_workflows_ts_no_new_date():
    with open(WORKFLOWS_FILE) as f:
        content = f.read()
    assert not re.search(r"new Date\(", content), (
        "src/workflows.ts must NOT contain 'new Date(' after the fix."
    )


def test_workflow_completed(workflow_handle):
    _, handle = workflow_handle

    async def _describe():
        return await handle.describe()

    desc = asyncio.run(_describe())
    assert desc.status == WorkflowExecutionStatus.COMPLETED, (
        f"Workflow {_workflow_id()} expected to be COMPLETED, got {desc.status!r}."
    )


def test_history_has_pick_discount_and_no_nope(workflow_handle):
    _, handle = workflow_handle

    async def _events():
        evts = []
        async for evt in handle.fetch_history_events():
            evts.append(evt)
        return evts

    events = asyncio.run(_events())

    scheduled_types = []
    for evt in events:
        attrs = getattr(evt, "activity_task_scheduled_event_attributes", None)
        if attrs is not None and attrs.activity_type and attrs.activity_type.name:
            scheduled_types.append(attrs.activity_type.name)

    assert "pickDiscount" in scheduled_types, (
        f"Expected an ActivityTaskScheduled event for 'pickDiscount', "
        f"got scheduled activity types: {scheduled_types}"
    )
    assert "nope" not in scheduled_types, (
        f"Did not expect an ActivityTaskScheduled event for activity type 'nope', "
        f"got scheduled activity types: {scheduled_types}"
    )


def test_workflow_result_discount(workflow_handle):
    _, handle = workflow_handle

    async def _result():
        return await handle.result()

    result = asyncio.run(_result())
    assert isinstance(result, dict), f"Workflow result must be a dict-like object, got: {type(result)!r}"
    assert "discount" in result, f"Workflow result missing 'discount' field: {result!r}"
    assert "userId" in result, f"Workflow result missing 'userId' field: {result!r}"
    assert "decidedAt" in result, f"Workflow result missing 'decidedAt' field: {result!r}"
    assert result["discount"] in VALID_DISCOUNTS, (
        f"Workflow discount {result['discount']!r} must be one of {sorted(VALID_DISCOUNTS)}."
    )
    assert isinstance(result["userId"], str), f"userId must be a string, got: {result['userId']!r}"
    assert isinstance(result["decidedAt"], (int, float)), (
        f"decidedAt must be a number (ms epoch), got: {result['decidedAt']!r}"
    )


def test_output_log_contains_discount(workflow_handle):
    _, handle = workflow_handle

    async def _result():
        return await handle.result()

    result = asyncio.run(_result())
    expected_discount = int(result["discount"])

    assert os.path.isfile(LOG_FILE), f"Expected log file {LOG_FILE} to exist."
    with open(LOG_FILE) as f:
        log_content = f.read()

    match = re.search(r"^Discount:\s*(\d+)\s*$", log_content, re.MULTILINE)
    assert match, (
        f"Expected log file {LOG_FILE} to contain a line like 'Discount: <number>'. "
        f"Got contents:\n{log_content}"
    )
    logged = int(match.group(1))
    assert logged == expected_discount, (
        f"Logged discount {logged} does not match Workflow result discount {expected_discount}."
    )
    assert logged in VALID_DISCOUNTS, (
        f"Logged discount {logged} must be one of {sorted(VALID_DISCOUNTS)}."
    )
