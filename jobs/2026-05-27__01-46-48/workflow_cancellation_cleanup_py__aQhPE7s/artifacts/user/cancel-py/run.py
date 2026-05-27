"""
Orchestration entry-point:
  • Starts the Temporal worker as a background asyncio task.
  • Runs the client logic (start → wait 3 s → cancel → await).
  • Shuts the worker down once the client is done.
"""

import asyncio
import os

from temporalio.client import Client, WorkflowFailureError
from temporalio.exceptions import CancelledError as TemporalCancelledError
from temporalio.worker import Worker

from activities import release_resources
from workflows import LongJobWorkflow

TASK_QUEUE = "cancel-py"


async def main() -> None:
    address = os.environ["TEMPORAL_ADDRESS"]
    namespace = os.environ["TEMPORAL_NAMESPACE"]
    api_key = os.environ["TEMPORAL_API_KEY"]
    run_id = os.environ["ZEALT_RUN_ID"]
    workflow_id = f"job-{run_id}"

    # --- Connect (shared client) ---
    client = await Client.connect(
        address,
        namespace=namespace,
        api_key=api_key,
        tls=True,
    )

    # --- Start worker in background ---
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[LongJobWorkflow],
        activities=[release_resources],
    )

    worker_task = asyncio.create_task(worker.run())
    print(f"Worker started, polling task queue '{TASK_QUEUE}'")

    try:
        # --- Client logic ---
        handle = await client.start_workflow(
            "LongJobWorkflow",
            "alpha",  # job_id argument
            id=workflow_id,
            task_queue=TASK_QUEUE,
        )
        print(f"Started workflow id={workflow_id}")

        # Wait ~3 seconds then cancel
        await asyncio.sleep(3)
        await handle.cancel()
        print("Cancellation requested")

        # Await the result; expect a CancelledError
        try:
            await handle.result()
            print("ERROR: workflow completed without cancellation")
            raise SystemExit(1)
        except WorkflowFailureError as exc:
            if isinstance(exc.cause, TemporalCancelledError):
                print("Workflow successfully cancelled (WorkflowFailureError -> CancelledError)")
            else:
                print(f"ERROR: workflow failed with unexpected cause: {exc.cause!r}")
                raise SystemExit(1)
        except asyncio.CancelledError:
            print("Workflow successfully cancelled (asyncio.CancelledError)")

        print("Client finished — workflow is CANCELED on Temporal Cloud")

    finally:
        # Shut down worker gracefully
        worker_task.cancel()
        try:
            await worker_task
        except (asyncio.CancelledError, Exception):
            pass
        print("Worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
