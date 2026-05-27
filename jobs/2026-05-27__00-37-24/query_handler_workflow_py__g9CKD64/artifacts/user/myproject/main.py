import asyncio
import os
import sys
from temporalio.client import Client
from temporalio.worker import Worker
from workflow import StatefulWorkflow

async def main():
    # Read environment variables
    zealt_run_id = os.getenv("ZEALT_RUN_ID")
    temporal_api_key = os.getenv("TEMPORAL_API_KEY")
    temporal_address = os.getenv("TEMPORAL_ADDRESS")
    temporal_namespace = os.getenv("TEMPORAL_NAMESPACE")

    if not all([zealt_run_id, temporal_api_key, temporal_address, temporal_namespace]):
        print("Missing required environment variables")
        sys.exit(1)

    # Connect to Temporal Cloud
    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True,
    )

    # Start the Worker in the background
    task_queue = "query-handler-py"
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[StatefulWorkflow],
    )
    
    worker_task = asyncio.create_task(worker.run())

    try:
        # Start the Workflow
        workflow_id = f"query-wf-{zealt_run_id}"
        handle = await client.start_workflow(
            StatefulWorkflow.run,
            id=workflow_id,
            task_queue=task_queue,
        )

        # Wait briefly (approx 2 seconds) so counter increments
        await asyncio.sleep(2.5)

        # Mid-run Query
        mid_counter = await handle.query(StatefulWorkflow.get_counter)
        print(f"Mid counter: {mid_counter}")

        # Send Signal to finish
        await handle.signal(StatefulWorkflow.finish)

        # Await final result
        final_counter = await handle.result()
        print(f"Final counter: {final_counter}")

    finally:
        # Stop the worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
