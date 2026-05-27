import asyncio
import os
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Activity definition
@activity.defn(name="greet")
async def greet(name: str) -> str:
    return f"Hello, {name}!"

# Workflow definition
@workflow.defn(name="HelloWorkflow")
class HelloWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            greet,
            name,
            start_to_close_timeout=timedelta(seconds=5),
        )

async def main():
    # Load environment variables
    temporal_address = os.environ.get("TEMPORAL_ADDRESS")
    temporal_namespace = os.environ.get("TEMPORAL_NAMESPACE")
    temporal_api_key = os.environ.get("TEMPORAL_API_KEY")
    zealt_run_id = os.environ.get("ZEALT_RUN_ID")

    if not all([temporal_address, temporal_namespace, temporal_api_key, zealt_run_id]):
        missing = [v for v in ["TEMPORAL_ADDRESS", "TEMPORAL_NAMESPACE", "TEMPORAL_API_KEY", "ZEALT_RUN_ID"] if not os.environ.get(v)]
        print(f"Error: Missing environment variables: {', '.join(missing)}")
        return

    # Connect to Temporal Cloud
    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    task_queue = "hello-world-py"
    workflow_id = f"hello-wf-{zealt_run_id}"

    # Initialize Worker
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[HelloWorkflow],
        activities=[greet],
    )

    # Run Worker and Client in the same event loop
    # We start the worker in the background
    worker_task = asyncio.create_task(worker.run())

    try:
        # Start and wait for workflow result
        result = await client.execute_workflow(
            HelloWorkflow.run,
            "Temporal",
            id=workflow_id,
            task_queue=task_queue,
        )
        # Print the result to stdout as required
        print(result)
    finally:
        # Gracefully shut down the worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
