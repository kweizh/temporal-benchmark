import asyncio
import os
import sys
from temporalio.client import Client, TlsConfig
from temporalio.worker import Worker

from activities import notify
from workflows import ReminderWorkflow

async def main():
    # Read environment variables
    temporal_address = os.environ.get("TEMPORAL_ADDRESS")
    temporal_namespace = os.environ.get("TEMPORAL_NAMESPACE")
    temporal_api_key = os.environ.get("TEMPORAL_API_KEY")
    zealt_run_id = os.environ.get("ZEALT_RUN_ID")

    if not all([temporal_address, temporal_namespace, temporal_api_key, zealt_run_id]):
        print("Missing required environment variables.")
        sys.exit(1)

    # Connect to Temporal Cloud
    client = await Client.connect(
        temporal_address,
        namespace=temporal_namespace,
        api_key=temporal_api_key,
        tls=True
    )

    # Task queue name
    task_queue = "reminder-py"

    # Start Worker in the background
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=[ReminderWorkflow],
        activities=[notify],
    )
    
    # Run worker in background
    worker_task = asyncio.create_task(worker.run())

    try:
        # Start and wait for workflow completion
        workflow_id = f"reminder-py-{zealt_run_id}"
        
        result = await client.execute_workflow(
            ReminderWorkflow.run,
            args=["wake up", 3],
            id=workflow_id,
            task_queue=task_queue,
        )

        # Print result to stdout
        print(result)
        
    finally:
        # Shut down worker
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    asyncio.run(main())
