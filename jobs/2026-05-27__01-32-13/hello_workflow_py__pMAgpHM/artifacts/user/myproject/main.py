import asyncio
import contextlib
import os
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

TASK_QUEUE = "hello-world-py"


@activity.defn(name="greet")
async def greet(name: str) -> str:
    return f"Hello, {name}!"


@workflow.defn(name="HelloWorkflow")
class HelloWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            greet,
            name,
            start_to_close_timeout=timedelta(seconds=10),
        )


async def connect_client() -> Client:
    temporal_address = os.environ["TEMPORAL_ADDRESS"]
    temporal_namespace = os.environ["TEMPORAL_NAMESPACE"]
    temporal_api_key = os.environ["TEMPORAL_API_KEY"]

    return await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )


async def run_worker(client: Client) -> None:
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[HelloWorkflow],
        activities=[greet],
    )
    await worker.run()


async def main() -> None:
    zealt_run_id = os.environ.get("ZEALT_RUN_ID")
    if not zealt_run_id:
        raise RuntimeError("ZEALT_RUN_ID environment variable is required")

    workflow_id = f"hello-wf-{zealt_run_id}"

    client = await connect_client()

    worker_task = asyncio.create_task(run_worker(client))
    try:
        result = await client.execute_workflow(
            HelloWorkflow.run,
            "Temporal",
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
        print(result)
    finally:
        worker_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await worker_task


if __name__ == "__main__":
    asyncio.run(main())
