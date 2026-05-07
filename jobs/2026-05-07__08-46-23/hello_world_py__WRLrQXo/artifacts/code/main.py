import asyncio
import os
from temporalio import workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Define the workflow
@workflow.defn
class HelloWorldWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return f"Hello, {name}!"

async def main():
    # Get environment variables
    address = os.getenv("TEMPORAL_ADDRESS")
    namespace = os.getenv("TEMPORAL_NAMESPACE")
    api_key = os.getenv("TEMPORAL_API_KEY")

    if not address or not namespace or not api_key:
        print("Error: TEMPORAL_ADDRESS, TEMPORAL_NAMESPACE, and TEMPORAL_API_KEY must be set.")
        return

    # Connect to Temporal Cloud
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
    )

    # Task queue name
    task_queue = "hello-world-tasks"

    # Start the worker
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[HelloWorldWorkflow],
    )

    # Run the worker and the client concurrently
    # We use a task for the worker so we can shut it down later
    worker_task = asyncio.create_task(worker.run())

    try:
        # Execute the workflow
        result = await client.execute_workflow(
            HelloWorldWorkflow.run,
            "World",
            id="hello-world-wf",
            task_queue=task_queue,
        )
        print(result)
    finally:
        # Shut down the worker
        # In a real app, you might want to wait for the worker to finish processing
        # but here we just want to exit cleanly.
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
