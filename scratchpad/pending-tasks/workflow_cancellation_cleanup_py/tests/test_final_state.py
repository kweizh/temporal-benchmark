import asyncio
import os
import re

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

OUTPUT_FILE = "/workspace/cleanup.log"


def _run_id() -> str:
    rid = os.environ.get("ZEALT_RUN_ID")
    assert rid, "ZEALT_RUN_ID environment variable is not set in the verifier."
    return rid


def _required_env(name: str) -> str:
    value = os.environ.get(name)
    assert value, f"Environment variable {name} is not set in the verifier."
    return value


async def _connect_client() -> Client:
    address = _required_env("TEMPORAL_ADDRESS")
    namespace = _required_env("TEMPORAL_NAMESPACE")
    api_key = _required_env("TEMPORAL_API_KEY")
    return await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )


def test_cleanup_log_contains_released_alpha():
    assert os.path.isfile(OUTPUT_FILE), (
        f"Expected cleanup log {OUTPUT_FILE} to exist after task completion."
    )
    with open(OUTPUT_FILE, "r") as f:
        content = f.read()
    assert re.search(r"(^|\n)\s*released:alpha\s*(\n|$)", content), (
        f"Expected {OUTPUT_FILE} to contain a line 'released:alpha'. "
        f"Got:\n{content!r}"
    )


def test_workflow_canceled_on_temporal_cloud():
    async def _check():
        client = await _connect_client()
        workflow_id = f"job-{_run_id()}"
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()
        assert desc.status == WorkflowExecutionStatus.CANCELED, (
            f"Workflow {workflow_id} is not CANCELED on Temporal Cloud; "
            f"status={desc.status!r}."
        )
        assert desc.workflow_type == "LongJobWorkflow", (
            f"Expected workflow type 'LongJobWorkflow', "
            f"got {desc.workflow_type!r}."
        )
        assert desc.task_queue == "cancel-py", (
            f"Expected workflow task queue 'cancel-py', "
            f"got {desc.task_queue!r}."
        )

    asyncio.run(_check())


def test_release_resources_activity_scheduled_in_history():
    async def _check():
        client = await _connect_client()
        workflow_id = f"job-{_run_id()}"
        handle = client.get_workflow_handle(workflow_id)
        history = await handle.fetch_history()

        scheduled_activity_names = []
        for event in history.events:
            # 10 == EVENT_TYPE_ACTIVITY_TASK_SCHEDULED
            if int(event.event_type) == 10:
                attrs = event.activity_task_scheduled_event_attributes
                scheduled_activity_names.append(attrs.activity_type.name)

        assert "release_resources" in scheduled_activity_names, (
            "Expected workflow history to contain an ActivityTaskScheduled "
            f"event for activity type 'release_resources'. "
            f"Found scheduled activities: {scheduled_activity_names!r}."
        )

    asyncio.run(_check())
