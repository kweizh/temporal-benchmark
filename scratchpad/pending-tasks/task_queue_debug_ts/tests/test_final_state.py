import asyncio
import os
import re

import pytest
from temporalio.client import Client

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
WORKER_SRC = os.path.join(PROJECT_DIR, "src", "worker.ts")
CLIENT_SRC = os.path.join(PROJECT_DIR, "src", "client.ts")
WORKFLOW_TYPE = "PingWorkflow"
EXPECTED_RESULT = "pong-temporal"

_TASK_QUEUE_RE = re.compile(r"""taskQueue\s*:\s*['"]([^'"]+)['"]""")


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is required."
    return run_id


def _workflow_id() -> str:
    return f"ping-{_run_id()}"


def _extract_task_queue(path: str) -> str:
    with open(path) as f:
        content = f.read()
    match = _TASK_QUEUE_RE.search(content)
    assert match, (
        f"Could not find a `taskQueue: '...'` literal in {path}. "
        "The fix must keep an explicit task queue string in this file."
    )
    return match.group(1)


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


def test_worker_and_client_use_same_task_queue():
    worker_q = _extract_task_queue(WORKER_SRC)
    client_q = _extract_task_queue(CLIENT_SRC)
    assert worker_q == client_q, (
        f"Worker is registered on task queue '{worker_q}' but Client starts workflows "
        f"on '{client_q}'. They must match so the Worker can pick up the workflow."
    )


def test_log_file_contains_result():
    assert os.path.isfile(LOG_FILE), f"Expected log file at {LOG_FILE}."
    with open(LOG_FILE) as f:
        content = f.read()
    pattern = re.compile(r"Workflow result:\s*pong-temporal")
    assert pattern.search(content), (
        f"Expected log file {LOG_FILE} to contain a line matching "
        f"'Workflow result: {EXPECTED_RESULT}'. Got: {content!r}"
    )


def test_workflow_completed_with_expected_metadata():
    async def _check():
        client = await _connect()
        handle = client.get_workflow_handle(_workflow_id())
        return await handle.describe()

    desc = asyncio.run(_check())
    assert desc.status is not None and desc.status.name == "COMPLETED", (
        f"Expected workflow {_workflow_id()} status COMPLETED, got {desc.status}."
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
