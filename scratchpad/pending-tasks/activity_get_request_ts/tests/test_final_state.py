import asyncio
import os
import re

import pytest
from temporalio.client import Client

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
TASK_QUEUE = "repo-fetch-ts"
WORKFLOW_TYPE = "FetchRepoWorkflow"
EXPECTED_RESULT = "temporalio/temporal"


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is required."
    return run_id


def _workflow_id() -> str:
    return f"repo-fetch-{_run_id()}"


async def _connect() -> Client:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    return await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )


def test_log_file_contains_result():
    assert os.path.isfile(LOG_FILE), f"Expected log file at {LOG_FILE}."
    with open(LOG_FILE) as f:
        content = f.read()
    pattern = re.compile(r"Workflow result:\s*temporalio/temporal")
    assert pattern.search(content), (
        f"Expected log file {LOG_FILE} to contain a line matching "
        f"'Workflow result: {EXPECTED_RESULT}'. Got: {content!r}"
    )


def test_workflow_completed_with_expected_metadata():
    async def _check():
        client = await _connect()
        handle = client.get_workflow_handle(_workflow_id())
        desc = await handle.describe()
        return desc

    desc = asyncio.run(_check())
    assert desc.status is not None and desc.status.name == "COMPLETED", (
        f"Expected workflow {_workflow_id()} status COMPLETED, got {desc.status}."
    )
    assert desc.task_queue == TASK_QUEUE, (
        f"Expected workflow task queue {TASK_QUEUE}, got {desc.task_queue}."
    )
    assert desc.workflow_type == WORKFLOW_TYPE, (
        f"Expected workflow type {WORKFLOW_TYPE}, got {desc.workflow_type}."
    )


def test_workflow_result_matches_expected():
    async def _result():
        client = await _connect()
        handle = client.get_workflow_handle(_workflow_id())
        return await handle.result()

    result = asyncio.run(_result())
    assert result == EXPECTED_RESULT, (
        f"Expected workflow result '{EXPECTED_RESULT}', got '{result}'."
    )
