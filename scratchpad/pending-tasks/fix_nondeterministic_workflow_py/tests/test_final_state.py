import asyncio
import json
import os
import re

import pytest

PROJECT_DIR = "/home/user/discount-py"
WORKFLOWS_FILE = os.path.join(PROJECT_DIR, "workflows.py")
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
ALLOWED_DISCOUNTS = {0, 5, 10, 15, 20}


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is not set."
    return run_id


def _workflow_id() -> str:
    return f"discount-py-{_run_id()}"


def _read_log_result() -> dict:
    assert os.path.isfile(LOG_FILE), f"Log file {LOG_FILE} was not produced."
    with open(LOG_FILE) as f:
        content = f.read()
    match = re.search(r"Workflow result:\s*(\{.*\})", content)
    assert match, (
        f"Log file {LOG_FILE} does not contain a 'Workflow result: <json>' line. Got:\n{content}"
    )
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"Could not parse the workflow result as JSON from log: {match.group(1)} ({e})"
        )
    return data


# ---------------------------------------------------------------------------
# Static checks against workflows.py
# ---------------------------------------------------------------------------


def test_workflows_file_has_no_datetime_now():
    with open(WORKFLOWS_FILE) as f:
        content = f.read()
    assert not re.search(r"datetime\.datetime\.now|datetime\.now", content), (
        "workflows.py still contains datetime.now() / datetime.datetime.now() — "
        "the workflow must use workflow.now() for deterministic time."
    )


def test_workflows_file_has_no_random_choice():
    with open(WORKFLOWS_FILE) as f:
        content = f.read()
    assert not re.search(r"random\.choice", content), (
        "workflows.py still contains random.choice() — randomness must be moved into an Activity."
    )


def test_workflows_file_uses_pick_discount_activity():
    with open(WORKFLOWS_FILE) as f:
        content = f.read()
    assert "pick_discount" in content, (
        "workflows.py must reference the 'pick_discount' Activity."
    )
    assert re.search(r"workflow\.execute_activity", content), (
        "workflows.py must call workflow.execute_activity to invoke the Activity."
    )


# ---------------------------------------------------------------------------
# Log file checks
# ---------------------------------------------------------------------------


def test_log_file_contains_valid_result():
    data = _read_log_result()
    for field in ("user_id", "discount", "decided_at"):
        assert field in data, f"Workflow result is missing field '{field}': {data}"
    assert isinstance(data["discount"], int), (
        f"discount must be an int, got {type(data['discount']).__name__}: {data['discount']}"
    )
    assert data["discount"] in ALLOWED_DISCOUNTS, (
        f"discount must be one of {sorted(ALLOWED_DISCOUNTS)}, got {data['discount']}"
    )


# ---------------------------------------------------------------------------
# Temporal Cloud checks
# ---------------------------------------------------------------------------


def _connect_client():
    from temporalio.client import Client

    address = os.environ.get("TEMPORAL_ADDRESS")
    namespace = os.environ.get("TEMPORAL_NAMESPACE")
    api_key = os.environ.get("TEMPORAL_API_KEY")
    assert address and namespace and api_key, (
        "TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must all be set."
    )
    return Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )


@pytest.fixture(scope="module")
def temporal_client():
    return asyncio.get_event_loop().run_until_complete(_connect_client())


def test_workflow_completed_on_cloud(temporal_client):
    from temporalio.client import WorkflowExecutionStatus

    async def _describe():
        handle = temporal_client.get_workflow_handle(_workflow_id())
        return await handle.describe()

    desc = asyncio.get_event_loop().run_until_complete(_describe())
    assert desc.status == WorkflowExecutionStatus.COMPLETED, (
        f"Workflow {_workflow_id()} is not COMPLETED. status={desc.status}"
    )
    assert desc.task_queue == "discount-py", (
        f"Workflow {_workflow_id()} ran on task queue '{desc.task_queue}', expected 'discount-py'."
    )


def test_workflow_history_has_pick_discount_activity(temporal_client):
    async def _collect():
        handle = temporal_client.get_workflow_handle(_workflow_id())
        events = []
        async for evt in handle.fetch_history_events():
            events.append(evt)
        return events

    events = asyncio.get_event_loop().run_until_complete(_collect())
    scheduled = []
    for evt in events:
        attrs = getattr(evt, "activity_task_scheduled_event_attributes", None)
        if attrs and attrs.activity_type and attrs.activity_type.name:
            scheduled.append(attrs.activity_type.name)
    assert "pick_discount" in scheduled, (
        f"Workflow history is missing an ActivityTaskScheduled event for 'pick_discount'. "
        f"Scheduled activities: {scheduled}"
    )


def test_workflow_result_matches_log(temporal_client):
    async def _result():
        handle = temporal_client.get_workflow_handle(_workflow_id())
        return await handle.result()

    cloud_result = asyncio.get_event_loop().run_until_complete(_result())
    assert isinstance(cloud_result, dict), (
        f"Workflow result from Cloud must be a dict, got {type(cloud_result).__name__}"
    )
    assert cloud_result.get("discount") in ALLOWED_DISCOUNTS, (
        f"Cloud workflow discount {cloud_result.get('discount')} not in {sorted(ALLOWED_DISCOUNTS)}"
    )
    log_result = _read_log_result()
    assert cloud_result.get("discount") == log_result.get("discount"), (
        f"Discount mismatch between Cloud ({cloud_result.get('discount')}) and "
        f"log file ({log_result.get('discount')})."
    )
