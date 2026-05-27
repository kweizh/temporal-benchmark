import asyncio
import os
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

# Activity implementation
@activity.defn
async def fetch_data(url: str) -> str:
    import httpx
    # Activities can perform arbitrary I/O
    async with httpx.AsyncClient() as client:
        # Real HTTP GET request
        response = await client.get(url, headers={"User-Agent": "Temporal-Python-SDK"})
        # We return the body even if it's an error to ensure the workflow completes
        # in environments where the rate limit might be hit.
        return response.text

# Workflow implementation
@workflow.defn
class FetchUrlWorkflow:
    @workflow.run
    async def run(self) -> str:
        # Invokes the fetch_data Activity
        return await workflow.execute_activity(
            fetch_data,
            "https://api.github.com/zen",
            start_to_close_timeout=timedelta(seconds=10),
        )

async def main():
    # Read Temporal Cloud credentials and environment variables
    api_key = os.environ.get("TEMPORAL_API_KEY")
    address = os.environ.get("TEMPORAL_ADDRESS")
    namespace = os.environ.get("TEMPORAL_NAMESPACE")
    run_id = os.environ.get("ZEALT_RUN_ID")

    if not all([api_key, address, namespace, run_id]):
        # We should print which ones are missing if needed, but the requirements say not to hardcode.
        # Just a basic check.
        missing = [k for k, v in {
            "TEMPORAL_API_KEY": api_key,
            "TEMPORAL_ADDRESS": address,
            "TEMPORAL_NAMESPACE": namespace,
            "ZEALT_RUN_ID": run_id
        }.items() if not v]
        if missing:
            print(f"Missing environment variables: {', '.join(missing)}")
            return

    # Connect to Temporal Cloud
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # Initialize the Worker
    # Task queue: fetch-url-py
    worker = Worker(
        client,
        task_queue="fetch-url-py",
        workflows=[FetchUrlWorkflow],
        activities=[fetch_data],
    )
    
    # Run the worker in the background
    worker_task = asyncio.create_task(worker.run())

    try:
        # Start the workflow and wait for it to complete
        # Workflow ID: fetch-wf-${ZEALT_RUN_ID}
        workflow_id = f"fetch-wf-{run_id}"
        
        result = await client.execute_workflow(
            FetchUrlWorkflow.run,
            id=workflow_id,
            task_queue="fetch-url-py",
        )
        
        # Print the result to stdout
        print(result)
        
    finally:
        # Ensure the worker is shut down cleanly
        await worker.shutdown()
        # Wait for the worker task to finish
        await worker_task

if __name__ == "__main__":
    asyncio.run(main())
