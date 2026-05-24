import asyncio
import os
from temporalio.client import Client
from temporalio.worker import Worker
from activities import fetch_url
from workflows import ParallelFetchWorkflow

async def main():
    # Read environment variables
    temporal_address = os.environ.get("TEMPORAL_ADDRESS")
    temporal_namespace = os.environ.get("TEMPORAL_NAMESPACE")
    temporal_api_key = os.environ.get("TEMPORAL_API_KEY")
    zealt_run_id = os.environ.get("ZEALT_RUN_ID")

    if not all([temporal_address, temporal_namespace, temporal_api_key, zealt_run_id]):
        print("Error: Missing required environment variables.")
        return

    # Connect to Temporal Cloud
    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    # Define task queue
    task_queue = "parallel-py"

    # Start Worker
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[ParallelFetchWorkflow],
        activities=[fetch_url],
    )

    # Run worker in background and execute workflow
    worker_task = asyncio.create_task(worker.run())

    try:
        # Execute workflow
        urls = [
            "https://www.example.com",
            "https://api.github.com",
            "https://httpbin.org/status/200"
        ]
        
        result = await client.execute_workflow(
            ParallelFetchWorkflow.run,
            urls,
            id=f"parallel-{zealt_run_id}",
            task_queue=task_queue,
        )

        # Print result to stdout
        print(result)

    finally:
        # Shutdown worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
