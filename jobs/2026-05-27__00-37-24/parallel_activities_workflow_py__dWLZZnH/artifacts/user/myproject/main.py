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
        raise ValueError("Missing required environment variables")

    # Connect to Temporal Cloud
    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    # Run worker in the background
    worker = Worker(
        client,
        task_queue="parallel-py",
        workflows=[ParallelFetchWorkflow],
        activities=[fetch_url],
    )

    # Start the worker and the workflow client
    async with worker:
        urls = [
            "https://www.example.com",
            "https://api.github.com",
            "https://httpbin.org/status/200",
        ]
        
        result = await client.execute_workflow(
            ParallelFetchWorkflow.run,
            urls,
            id=f"parallel-{zealt_run_id}",
            task_queue="parallel-py",
        )

        print(result)

if __name__ == "__main__":
    asyncio.run(main())
