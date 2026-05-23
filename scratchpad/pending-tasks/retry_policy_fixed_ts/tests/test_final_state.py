import asyncio
import os
import re

import pytest
from temporalio.client import Client

PROJECT_DIR = "/home/user/myproject"
LOG_FILE = os.path.join(PROJECT_DIR, "output.log")
ATTEMPTS_LOG = "/workspace/attempts.log"
TASK_QUEUE = "retry-ts"
WORKFLOW_TYPE = "FlakyWorkflow"
EXPECTED_RESULT = "failed after 5 attempts"
EXPECTED_ATTEMPTS = 5


def _run_id() -> str:
    run_id = os.environ.get("ZEALT_RUN_ID")
    assert run_id, "ZEALT_RUN_ID environment variable is required."
    return run_id


def _workflow_id() -> str:
    return f"retry-{_run_id()}"


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


def test_output_log_contains_expected_result():
    assert os.path.isfile(LOG_FILE), f"Expected log file at {LOG_FILE}."
    with open(LOG_FILE) as f:
        content = f.read()
    pattern = re.compile(r"Workflow result:\s*failed after 5 attempts")
    assert pattern.search(content), (
        f"Expected log file {LOG_FILE} to contain a line matching "
        f"'Workflow result: {EXPECTED_RESULT}'. Got: {content!r}"
    )


def test_attempts_log_has_exactly_five_lines():
    assert os.path.isfile(ATTEMPTS_LOG), (
        f"Expected attempts log file at {ATTEMPTS_LOG}."
    )
    with open(ATTEMPTS_LOG) as f:
        lines = [line for line in f.read().splitlines() if line.strip()]
    assert len(lines) == EXPECTED_ATTEMPTS, (
        f"Expected {ATTEMPTS_LOG} to contain exactly {EXPECTED_ATTEMPTS} non-empty "
        f"lines (one per Activity attempt), got {len(lines)}: {lines!r}"
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
