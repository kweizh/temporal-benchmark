import asyncio
import os
import subprocess

import pytest
from temporalio.client import Client, WorkflowExecutionStatus

PROJECT_DIR = "/home/user/myproject"
EXPECTED_URLS = [
    "https://www.example.com",
    "https://api.github.com",
    "https://httpbin.org/status/200",
]


def _get_env(name: str) -> str:
    value = os.environ.get(name)
    assert value is not None and value != "", \
        f"Environment variable {name} must be set for the verifier."
    return value


@pytest.fixture(scope="module")
def python_main_output() -> subprocess.CompletedProcess:
    """Run `python main.py` once and reuse its output across tests."""
    env = os.environ.copy()
    result = subprocess.run(
        ["python", "main.py"],
        cwd=PROJECT_DIR,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,
    )
    return result


def test_python_main_succeeds(python_main_output: subprocess.CompletedProcess):
    assert python_main_output.returncode == 0, (
        "`python main.py` did not exit successfully. "
        f"stdout=\n{python_main_output.stdout}\nstderr=\n{python_main_output.stderr}"
    )


def test_python_main_prints_all_urls(
    python_main_output: subprocess.CompletedProcess,
):
    combined = (python_main_output.stdout or "") + (python_main_output.stderr or "")
    for url in EXPECTED_URLS:
        assert url in combined, (
            f"Expected combined output of `python main.py` to contain {url!r}, "
            f"got stdout=\n{python_main_output.stdout}\nstderr=\n{python_main_output.stderr}"
        )


async def _verify_workflow_in_cloud() -> dict:
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

    workflow_id = f"parallel-{run_id}"
    handle = client.get_workflow_handle(workflow_id)

    description = await handle.describe()
    assert description.workflow_type == "ParallelFetchWorkflow", (
        f"Expected workflow type 'ParallelFetchWorkflow' for workflow id '{workflow_id}', "
        f"got: {description.workflow_type!r}"
    )
    assert description.status == WorkflowExecutionStatus.COMPLETED, (
        f"Expected workflow '{workflow_id}' to have status COMPLETED, "
        f"got: {description.status}"
    )

    result = await handle.result()
    assert isinstance(result, dict), (
        f"Expected workflow result to be a dict, got: {type(result).__name__}={result!r}"
    )
    for url in EXPECTED_URLS:
        assert url in result, (
            f"Expected workflow result dict to contain key {url!r}, got: {result!r}"
        )
        assert int(result[url]) == 200, (
            f"Expected workflow result[{url!r}] to be 200, got: {result[url]!r}"
        )

    # Inspect history to confirm fan-out parallelism via asyncio.gather.
    history = await handle.fetch_history()
    scheduled_times = []
    for event in history.events:
        attrs = getattr(event, "activity_task_scheduled_event_attributes", None)
        if attrs is None:
            continue
        # Some serializations leave the field present but empty; check activity_type.
        activity_type_name = getattr(getattr(attrs, "activity_type", None), "name", "")
        if activity_type_name == "fetch_url":
            scheduled_times.append(event.event_time)

    assert len(scheduled_times) == 3, (
        f"Expected exactly 3 ACTIVITY_TASK_SCHEDULED events for activity 'fetch_url', "
        f"got {len(scheduled_times)}."
    )

    epoch_seconds = [t.ToMicroseconds() / 1e6 for t in scheduled_times]
    spread = max(epoch_seconds) - min(epoch_seconds)
    assert spread <= 5.0, (
        f"Expected all 3 'fetch_url' activities to be scheduled in parallel within 5 seconds, "
        f"observed spread of {spread:.3f} seconds across event times: {scheduled_times}."
    )

    return result


def test_workflow_completed_in_temporal_cloud(
    python_main_output: subprocess.CompletedProcess,
):
    assert python_main_output.returncode == 0, (
        "Skipping cloud verification because `python main.py` did not exit cleanly."
    )
    asyncio.run(_verify_workflow_in_cloud())
