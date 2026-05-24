import asyncio
import glob
import os
import re

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

LOG_FILE = "/workspace/loop.log"
OUT_FILE = "/workspace/loop.out"
PROJECT_DIR = "/home/user/loop-py"


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


def test_loop_log_has_25_lines_with_values_1_to_25():
    assert os.path.isfile(LOG_FILE), (
        f"Expected log file {LOG_FILE} to exist after task completion."
    )
    with open(LOG_FILE, "r") as f:
        raw = f.read()
    # Split into lines, dropping a trailing empty entry from a final newline.
    parts = raw.split("\n")
    if parts and parts[-1] == "":
        parts = parts[:-1]
    assert len(parts) == 25, (
        f"Expected exactly 25 lines in {LOG_FILE}; got {len(parts)} lines. "
        f"File content:\n{raw!r}"
    )
    parsed = []
    for idx, line in enumerate(parts, start=1):
        stripped = line.strip()
        try:
            parsed.append(int(stripped))
        except ValueError:
            pytest.fail(
                f"Line {idx} of {LOG_FILE} is not an integer: {line!r} "
                f"(full content: {raw!r})"
            )
    assert parsed == list(range(1, 26)), (
        f"Expected {LOG_FILE} to contain integers 1..25 in order; got {parsed!r}."
    )


def test_loop_out_contains_result_25():
    assert os.path.isfile(OUT_FILE), (
        f"Expected output file {OUT_FILE} to exist after task completion."
    )
    with open(OUT_FILE, "r") as f:
        content = f.read()
    assert re.search(r"(^|\n)\s*result=25\s*(\n|$)", content), (
        f"Expected {OUT_FILE} to contain a line 'result=25'. Got:\n{content!r}"
    )


def test_workflow_source_uses_continue_as_new():
    assert os.path.isdir(PROJECT_DIR), (
        f"Project directory {PROJECT_DIR} does not exist."
    )
    py_files = glob.glob(os.path.join(PROJECT_DIR, "**", "*.py"), recursive=True)
    assert py_files, (
        f"No Python source files found under {PROJECT_DIR}; "
        f"cannot verify continue_as_new usage."
    )
    found = False
    for path in py_files:
        try:
            with open(path, "r") as f:
                if "continue_as_new" in f.read():
                    found = True
                    break
        except OSError:
            continue
    assert found, (
        f"Expected at least one Python source file under {PROJECT_DIR} to contain "
        f"the substring 'continue_as_new'."
    )


def test_workflow_completed_on_temporal_cloud():
    async def _check():
        client = await _connect_client()
        workflow_id = f"loop-py-{_run_id()}"
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()
        assert desc.status == WorkflowExecutionStatus.COMPLETED, (
            f"Workflow {workflow_id} is not COMPLETED on Temporal Cloud; "
            f"status={desc.status!r}."
        )
        assert desc.workflow_type == "LongLoopWorkflow", (
            f"Expected workflow type 'LongLoopWorkflow', "
            f"got {desc.workflow_type!r}."
        )
        assert desc.task_queue == "loop-py", (
            f"Expected workflow task queue 'loop-py', "
            f"got {desc.task_queue!r}."
        )

    asyncio.run(_check())


def test_workflow_result_is_25():
    async def _check():
        client = await _connect_client()
        workflow_id = f"loop-py-{_run_id()}"
        handle = client.get_workflow_handle(workflow_id)
        result = await handle.result()
        assert result == 25, (
            f"Expected workflow {workflow_id} to return 25 (target); got {result!r}."
        )

    asyncio.run(_check())


def test_workflow_chain_has_at_least_two_continued_as_new_runs():
    async def _check():
        client = await _connect_client()
        workflow_id = f"loop-py-{_run_id()}"
        # Escape any single quotes in the workflow id to safely embed in the query.
        safe_id = workflow_id.replace("'", "''")
        query = f"WorkflowId = '{safe_id}'"
        executions = []
        async for execution in client.list_workflows(query):
            executions.append(execution)
        assert executions, (
            f"Expected at least one workflow execution for {workflow_id} "
            f"on Temporal Cloud; list_workflows returned none."
        )
        continued = [
            e for e in executions
            if e.status == WorkflowExecutionStatus.CONTINUED_AS_NEW
        ]
        completed = [
            e for e in executions
            if e.status == WorkflowExecutionStatus.COMPLETED
        ]
        assert len(continued) >= 2, (
            f"Expected at least 2 runs in chain {workflow_id} to have status "
            f"CONTINUED_AS_NEW; got {len(continued)} "
            f"(statuses: {[e.status for e in executions]!r})."
        )
        assert len(completed) == 1, (
            f"Expected exactly 1 run in chain {workflow_id} to have status "
            f"COMPLETED; got {len(completed)} "
            f"(statuses: {[e.status for e in executions]!r})."
        )

    asyncio.run(_check())
