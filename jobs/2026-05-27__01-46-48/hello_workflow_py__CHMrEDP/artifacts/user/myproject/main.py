import asyncio
import os
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker


# ---------------------------------------------------------------------------
# Activity
# ---------------------------------------------------------------------------

@activity.defn(name="greet")
async def greet(name: str) -> str:
    return f"Hello, {name}!"


# ---------------------------------------------------------------------------
# Workflow
# ---------------------------------------------------------------------------

@workflow.defn(name="HelloWorkflow")
class HelloWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            greet,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

TASK_QUEUE = "hello-world-py"


def _get_env(key: str) -> str:
    value = os.environ.get(key)
    if not value:
        raise RuntimeError(f"Required environment variable '{key}' is not set")
    return value


async def connect_client() -> Client:
    """Create a client connected to Temporal Cloud via API key + TLS."""
    address = _get_env("TEMPORAL_ADDRESS")
    namespace = _get_env("TEMPORAL_NAMESPACE")
    api_key = _get_env("TEMPORAL_API_KEY")

    return await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )


# ---------------------------------------------------------------------------
# Main entrypoint
# ---------------------------------------------------------------------------

async def main() -> None:
    run_id = _get_env("ZEALT_RUN_ID")
    workflow_id = f"hello-wf-{run_id}"

    client = await connect_client()

    # Start the worker as a background task.
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[HelloWorkflow],
        activities=[greet],
    )

    worker_task = asyncio.create_task(worker.run())

    try:
        # Execute the workflow and wait for its result.
        result = await client.execute_workflow(
            HelloWorkflow.run,
            "Temporal",
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
        print(result)
    finally:
        # Cancel the worker gracefully once the workflow has finished.
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
