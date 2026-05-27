import asyncio
import os
import sys
from datetime import timedelta

from temporalio import activity, workflow
from temporalio.client import Client, TLSConfig, WorkflowFailureError
from temporalio.worker import Worker
from temporalio.exceptions import CancelledError

@activity.defn
async def release_resources(job_id: str) -> None:
    os.makedirs("/workspace", exist_ok=True)
    with open("/workspace/cleanup.log", "a") as f:
        f.write(f"released:{job_id}\n")

@workflow.defn
class LongJobWorkflow:
    @workflow.run
    async def run(self, job_id: str) -> None:
        try:
            await workflow.sleep(timedelta(minutes=10))
        except asyncio.CancelledError:
            await asyncio.shield(
                workflow.execute_activity(
                    release_resources,
                    job_id,
                    start_to_close_timeout=timedelta(seconds=30),
                )
            )
            raise

async def main():
    temporal_address = os.environ["TEMPORAL_ADDRESS"]
    temporal_namespace = os.environ["TEMPORAL_NAMESPACE"]
    temporal_api_key = os.environ["TEMPORAL_API_KEY"]
    zealt_run_id = os.environ.get("ZEALT_RUN_ID", "local")

    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    worker = Worker(
        client,
        task_queue="cancel-py",
        workflows=[LongJobWorkflow],
        activities=[release_resources],
    )

    async def run_client():
        workflow_id = f"job-{zealt_run_id}"
        
        handle = await client.start_workflow(
            LongJobWorkflow.run,
            "alpha",
            id=workflow_id,
            task_queue="cancel-py",
        )
        
        await asyncio.sleep(3)
        await handle.cancel()
        
        try:
            await handle.result()
        except WorkflowFailureError as e:
            if isinstance(e.cause, CancelledError):
                print("Workflow successfully cancelled.")
                sys.exit(0)
            else:
                raise

    # Start worker and client concurrently
    worker_task = asyncio.create_task(worker.run())
    
    try:
        await run_client()
    finally:
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
