import os
import asyncio
from datetime import timedelta
from temporalio import activity, workflow
from temporalio.client import Client
from temporalio.worker import Worker

with workflow.unsafe.imports_passed_through():
    import httpx

@activity.defn
async def fetch_data(url: str) -> str:
    async with httpx.AsyncClient() as client:
        # Add headers to act like a real user agent to sometimes avoid 403
        headers = {"User-Agent": "Temporalio-Python-SDK-Quickstart"}
        response = await client.get(url, headers=headers)
        return response.text

@workflow.defn
class FetchUrlWorkflow:
    @workflow.run
    async def run(self) -> str:
        return await workflow.execute_activity(
            fetch_data,
            "https://api.github.com/zen",
            start_to_close_timeout=timedelta(seconds=10),
        )

async def main():
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ["ZEALT_RUN_ID"]
    
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True
    )
    
    worker = Worker(
        client,
        task_queue="fetch-url-py",
        workflows=[FetchUrlWorkflow],
        activities=[fetch_data],
    )
    
    worker_task = asyncio.create_task(worker.run())
    
    try:
        result = await client.execute_workflow(
            FetchUrlWorkflow.run,
            id=f"fetch-wf-{run_id}",
            task_queue="fetch-url-py",
        )
        print(result)
    finally:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
