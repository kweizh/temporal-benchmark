import asyncio
import os
import re

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

OUTPUT_FILE = "/workspace/counter.out"


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


def test_output_file_exists_and_has_final_6():
    assert os.path.isfile(OUTPUT_FILE), (
        f"Expected output file {OUTPUT_FILE} to exist after task completion."
    )
    with open(OUTPUT_FILE, "r") as f:
        content = f.read()
    assert re.search(r"(^|\n)\s*final=6\s*(\n|$)", content), (
        f"Expected {OUTPUT_FILE} to contain a line 'final=6'. Got:\n{content!r}"
    )


def test_workflow_completed_on_temporal_cloud():
    async def _check():
        client = await _connect_client()
        workflow_id = f"counter-{_run_id()}"
        handle = client.get_workflow_handle(workflow_id)
        desc = await handle.describe()
        assert desc.status == WorkflowExecutionStatus.COMPLETED, (
            f"Workflow {workflow_id} is not COMPLETED on Temporal Cloud; "
            f"status={desc.status!r}."
        )
        assert desc.workflow_type == "CounterWorkflow", (
            f"Expected workflow type 'CounterWorkflow', "
            f"got {desc.workflow_type!r}."
        )
        assert desc.task_queue == "counter-py", (
            f"Expected workflow task queue 'counter-py', "
            f"got {desc.task_queue!r}."
        )

    asyncio.run(_check())


def test_workflow_result_is_six():
    async def _check():
        client = await _connect_client()
        workflow_id = f"counter-{_run_id()}"
        handle = client.get_workflow_handle(workflow_id)
        result = await handle.result()
        assert result == 6, (
            f"Expected workflow {workflow_id} to return 6 (1+2+3); got {result!r}."
        )

    asyncio.run(_check())
