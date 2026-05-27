"""
Entrypoint: starts the worker as a background asyncio task, executes the
ReminderWorkflow via the client, prints the result, then shuts everything down.
"""
import asyncio
import os
from temporalio.client import Client, TLSConfig
from temporalio.worker import Worker

from activities import notify
from workflows import ReminderWorkflow

TASK_QUEUE = "reminder-py"


async def main() -> None:
    # --- Read credentials from the environment ---
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ["ZEALT_RUN_ID"]

    workflow_id = f"reminder-py-{run_id}"

    # --- Connect to Temporal Cloud (API key + TLS) ---
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # --- Start the worker as a background task ---
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[ReminderWorkflow],
        activities=[notify],
    )
    worker_task = asyncio.create_task(worker.run())

    try:
        # --- Execute the workflow and wait for its result ---
        result = await client.execute_workflow(
            ReminderWorkflow.run,
            args=["wake up", 3],
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
        print(result)
    finally:
        # --- Gracefully shut down the worker ---
        worker_task.cancel()
        try:
            await worker_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(main())
