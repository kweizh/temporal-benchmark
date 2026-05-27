import asyncio
import os
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker


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


async def main():
    temporal_address = os.environ.get("TEMPORAL_ADDRESS")
    temporal_namespace = os.environ.get("TEMPORAL_NAMESPACE")
    temporal_api_key = os.environ.get("TEMPORAL_API_KEY")
    zealt_run_id = os.environ.get("ZEALT_RUN_ID", "default")
    
    # Connect client
    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    # Run the worker
    worker = Worker(
        client,
        task_queue="hello-world-py",
        workflows=[HelloWorkflow],
        activities=[greet],
    )
    
    # Start worker in background
    worker_task = asyncio.create_task(worker.run())
    
    # Execute workflow
    workflow_id = f"hello-wf-{zealt_run_id}"
    try:
        result = await client.execute_workflow(
            HelloWorkflow.run,
            "Temporal",
            id=workflow_id,
            task_queue="hello-world-py",
        )
        print(result)
    finally:
        # Cancel worker gracefully
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
